import json
import logging
import os
import re
import time
from typing import List, Dict, Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from downloader import downloader, postprocess
from updater import updater
from utils import config
from utils.notify import notifier
from utils.rename import rename_series
from utils.request import RequestHandler

log = logging.getLogger(__name__)
request = RequestHandler()


def get_headers(url):
    domain = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Referer": domain,
        "Origin": domain,
        "sec-fetch-mode": "no-cors"
    }


def extract_images_from_html(html_content: str) -> List[str]:
    pattern = r'let\s+urls\s*=\s*(\[.*?\])\s*;'
    match = re.search(pattern, html_content, re.DOTALL)

    images = []
    if match:
        try:
            json_str = match.group(1)
            images = json.loads(json_str)
        except json.JSONDecodeError:
            link_pattern = r'["\'](http[^"\']+)["\']'
            images = re.findall(link_pattern, match.group(1))

    return images


def get_total_pages(soup: BeautifulSoup) -> int:
    try:
        tag = soup.find(attrs={"title": re.compile(r"共\s*\d+\s*页")})
        if tag:
            title_text = tag.get("title")
            match = re.search(r"共\s*(\d+)\s*页", title_text)
            if match:
                return int(match.group(1))

        pg_div = soup.find("div", class_="pg")
        if pg_div:
            links = pg_div.find_all("a")
            max_page = 1
            for link in links:
                text = link.get_text(strip=True)
                if text.isdigit():
                    max_page = max(max_page, int(text))
                elif "page=" in link.get("href", ""):
                    href_match = re.search(r"page=(\d+)", link.get("href"))
                    if href_match:
                        max_page = max(max_page, int(href_match.group(1)))
            return max_page

    except Exception as e:
        log.warning(f"解析总页数失败，默认使用 1 页: {e}")

    return 1


def get_chapter_images(comic_id: str, zjid: str) -> tuple[str, List[str]]:
    base_url = f"https://www.antbyw.com/plugin.php?id=jameson_manhua&a=read&kuid={comic_id}&zjid={zjid}"

    log.info(f"正在分析第 1 页...")
    headers = get_headers(base_url)
    request.headers.update(headers)

    response = request.get(base_url)
    if not response:
        return "", []

    all_images = []

    images_p1 = extract_images_from_html(response.text)
    all_images.extend(images_p1)

    if not images_p1:
        log.warning(f"第 1 页未找到图片，可能需要登录或页面结构变更。")

    soup = BeautifulSoup(response.text, 'html.parser')
    total_pages = get_total_pages(soup)

    if total_pages > 1:
        log.info(f"检测到共 {total_pages} 页，开始获取剩余页面...")

        for page in range(2, total_pages + 1):
            page_url = f"{base_url}&page={page}"
            time.sleep(0.5)

            resp = request.get(page_url)
            if resp:
                imgs = extract_images_from_html(resp.text)
                if imgs:
                    all_images.extend(imgs)
                    log.debug(f"第 {page}/{total_pages} 页获取到 {len(imgs)} 张图片")
                else:
                    log.warning(f"第 {page} 页没有提取到图片")
            else:
                log.error(f"第 {page} 页请求失败")

    seen = set()
    unique_images = []
    for url in all_images:
        if url not in seen:
            unique_images.append(url)
            seen.add(url)

    if not unique_images:
        log.error(f"章节解析失败，未找到任何图片。JS片段检查: {response.text[:1000] if response else 'No Response'}")

    return base_url, unique_images


def download_chapter(task: Dict[str, Any], uuid: str, chapter_name: str):
    log.info(f"准备下载: {task['name']} - {chapter_name}")

    page_url, images = get_chapter_images(task['comic_id'], uuid)
    if not images:
        log.error(f"无法获取章节 {chapter_name} (ID: {uuid}) 的图片")
        notifier.add_error("antbyw", f"{task['name']} - {chapter_name}", "获取章节图片失败")
        return False

    save_path = os.path.join(config.DOWNLOAD_PATH, task['name'], chapter_name)
    os.makedirs(save_path, exist_ok=True)

    headers = get_headers(page_url)
    from downloader import request as dl_request
    old_headers = dl_request.headers.copy()
    dl_request.headers.update(headers)

    success_count = 0
    total_images = len(images)

    log.info(f"本章共 {total_images} 张图片，开始下载...")

    for index, img_url in enumerate(images):
        file_extension = os.path.splitext(urlparse(img_url).path)[1]
        if not file_extension or len(file_extension) > 5:
            if "webp" in img_url:
                file_extension = ".webp"
            else:
                file_extension = ".jpg"

        file_name = f"{index:04d}{file_extension}"
        save_file_path = os.path.join(save_path, file_name)

        if downloader(img_url, save_file_path):
            success_count += 1
            if index % 5 == 0 or index == total_images - 1:
                log.info(f"进度: {index + 1}/{total_images}")
        else:
            log.error(f"下载失败 {index:04d} - {img_url}")

    dl_request.headers = old_headers

    if success_count == 0:
        log.error(f"章节 {chapter_name} 下载失败，无图片成功下载")
        notifier.add_error("antbyw", f"{task['name']} - {chapter_name}", "所有图片下载失败")
        return False

    chapter_filename, chapter_num, is_special = rename_series(
        chapter_name, task['ep_pattern'], task['vol_pattern']
    )

    postprocess(
        task['name'], chapter_name,
        chapter_filename, chapter_num, save_path, is_special
    )

    updater.update_chapter_record(task['site'], task['comic_id'], chapter_name)

    notifier.add_success("antbyw", task['name'], chapter_name)

    return True


def download_task(task: Dict[str, Any]):
    if not task.get('chapter_infos'):
        return

    log.info(f"开始处理 {task['name']} 的 {len(task['chapter_infos'])} 个章节")

    for uuid, name in task['chapter_infos']:
        try:
            success = download_chapter(task, uuid, name)
            if not success:
                log.error(f"章节下载失败: {name}")
        except Exception as e:
            log.error(f"章节处理异常: {e}")
            notifier.add_error("antbyw", f"{task['name']} - {name}", str(e))
        time.sleep(2)

    log.info(f"{task['name']} 需要更新的下载已完成")


def download_batch(tasks: List[Dict[str, Any]]):
    if not tasks:
        log.info("当前没有需要更新的内容")
        return

    log.info(f"检测到 {len(tasks)} 个 Antbyw 任务")

    for task in tasks:
        infos = task.get('chapter_infos', [])
        debug_uuids = "\n".join([f"  - {uuid} ({name})" for uuid, name in infos])

        info = (
            f"漫画名称: {task['name']}\n"
            f"当前章节: {task['latest_chapter'] or '无'}\n"
            f"待更新数: {len(infos)}"
        )
        log.info(info)
        log.debug(f"UUID列表:\n{debug_uuids}")

        download_task(task)

    log.info("所有 Antbyw 下载任务已完成")

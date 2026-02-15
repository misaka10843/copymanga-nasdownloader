import json
import logging
import os
import time
from typing import List, Dict, Any

from bs4 import BeautifulSoup

from downloader import downloader, postprocess
from updater import updater
from utils import config
from utils.notify import notifier
from utils.request import RequestHandler

log = logging.getLogger(__name__)
request = RequestHandler()

BASE_URL = "https://www.ganganonline.com"


def get_chapter_images(comic_id: str, chapter_id: str):
    url = f"{BASE_URL}/title/{comic_id}/chapter/{chapter_id}"
    try:
        response = request.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find("script", {"id": "__NEXT_DATA__"})

        if not script_tag:
            return None

        data = json.loads(script_tag.string)
        pages = data['props']['pageProps']['data'].get('pages', [])

        image_list = []
        for page in pages:
            if 'image' in page:
                img_path = page['image'].get('imageUrl')
                if img_path:
                    # 补全完整 URL
                    image_list.append(f"{BASE_URL}{img_path}")

        return image_list

    except Exception as e:
        log.error(f"章节内容解析失败 (ID: {chapter_id})：{e}")
        return None


def download_chapter(task: Dict[str, Any], uuid: str, chapter_title: str, chapter_index: int):
    image_list = get_chapter_images(task['comic_id'], uuid)

    if not image_list:
        log.error(f"无法获取章节 {chapter_title} (ID: {uuid}) 的图片内容")
        notifier.add_error("ganganonline", f"{task['name']} - {chapter_title}", "获取章节图片内容失败")
        return False

    log.info(f"已获取到 {task['name']} {chapter_title} 的内容(共{len(image_list)}页)，开始安排下载")

    save_path = os.path.join(config.DOWNLOAD_PATH, task['name'], chapter_title)
    os.makedirs(save_path, exist_ok=True)

    download_failed = False
    for index, url in enumerate(image_list):
        image_path = os.path.join(save_path, f"{index:04d}.jpg")

        if downloader(url, image_path):
            log.info(f"已下载 {task['name']} {chapter_title} {index:04d}.jpg")
        else:
            log.error(f"下载失败: {task['name']} {chapter_title} {index:04d}.jpg")
            download_failed = True

    if download_failed:
        notifier.add_error("ganganonline", f"{task['name']} - {chapter_title}", "部分图片下载失败")

    log.info(f"{task['name']} {chapter_title} 下载完成，开始进行cbz打包")

    chapter_num = task['starting_index'] + chapter_index + 1
    chapter_filename = f"{chapter_num:04d} {chapter_title}"
    is_special = False

    postprocess(
        task['name'], chapter_title,
        chapter_filename, chapter_num, save_path, is_special
    )

    updater.update_chapter_record(
        task['site'], task['comic_id'], chapter_title
    )

    notifier.add_success("ganganonline", task['name'], chapter_title)
    log.info(f"{task['name']} {chapter_title} cbz打包完成")
    return True


def download_task(task: Dict[str, Any]):
    if not task.get('chapter_infos'):
        log.info(f"{task['name']} 没有待下载章节")
        return

    log.info(f"开始处理 {task['name']} 的 {len(task['chapter_infos'])} 个章节")

    for index, (uuid, name) in enumerate(task['chapter_infos']):
        try:
            success = download_chapter(task, uuid, name, index)
            if not success:
                log.error(f"章节下载失败: {task['name']} {name}, CID: {uuid}")
        except Exception as e:
            log.error(f"章节处理异常: {e}")
            notifier.add_error("ganganonline", f"{task['name']} - {name}", str(e))
        time.sleep(3)

    log.info(f"{task['name']} 需要更新的下载已完成")


def download_batch(tasks: List[Dict[str, Any]]):
    if not tasks:
        log.info("当前没有需要更新的内容")
        return

    log.info(f"检测到 {len(tasks)} 个漫画有更新内容")

    for task in tasks:
        debug_uuids = "\n".join([f"  - {uuid} ({name})" for uuid, name in task.get('chapter_infos', [])])

        info = (
            f"漫画名称: {task['name']}\n"
            f"当前章节: {task['latest_chapter'] or '无'}\n"
            f"待更新数: {len(task.get('chapter_infos', []))}"
        )
        log.info(info)
        log.debug(f"任务详情:\n{debug_uuids}")

        download_task(task)

    log.info("所有漫画下载任务已完成")

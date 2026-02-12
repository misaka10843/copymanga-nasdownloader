import logging
import os
import time
from typing import List, Dict, Any

from downloader import downloader, postprocess
from updater import updater
from utils import config
from utils.request import RequestHandler

log = logging.getLogger(__name__)
request = RequestHandler()


def get_chapter(comic_id: str, cid: str):
    """获取章节详情"""
    data = request.get(f"https://terra-historicus.hypergryph.com/api/comic/{comic_id}/episode/{cid}")
    try:
        return data.json()['data']
    except Exception as e:
        log.error(f"漫画章节内容解析失败：{e}")
        return None


def download_chapter(task: Dict[str, Any], uuid: str, chapter_title: str, chapter_index: int):
    """下载单个章节"""
    chapter = get_chapter(task['comic_id'], uuid)
    if not chapter:
        log.error(f"无法获取章节 {chapter_title} (CID: {uuid}) 的内容")
        return False

    log.info(f"已获取到 {task['name']} {chapter_title} 的内容，开始安排下载")

    image_list = []
    for i in range(len(chapter['pageInfos'])):
        try:
            data = request.get(
                f"https://terra-historicus.hypergryph.com/api/comic/{task['comic_id']}/episode/{uuid}/page?pageNum={i + 1}")
            image_list.append(data.json()['data']['url'])
        except Exception as e:
            log.error(f"漫画图片链接解析失败，为了防止下载不完整的漫画章节将退出程序：{e}")
            return False

    save_path = os.path.join(config.DOWNLOAD_PATH, task['name'], chapter_title)
    os.makedirs(save_path, exist_ok=True)

    # 下载所有图片
    for index, url in enumerate(image_list):
        image_path = os.path.join(save_path, f"{index:04d}.jpg")

        if downloader(url, image_path):
            log.info(f"已下载 {task['name']} {chapter_title} {index:04d}.jpg")
        else:
            log.error(f"下载失败: {task['name']} {chapter_title} {index:04d}.jpg")

    log.info(f"{task['name']} {chapter_title} 下载完成，开始进行cbz打包")

    chapter_filename = f"{task['starting_index'] + chapter_index + 1:04d} {chapter_title}"
    chapter_num = task['starting_index'] + chapter_index + 1
    is_special = False

    postprocess(
        task['name'], chapter_title,
        chapter_filename, chapter_num, save_path, is_special
    )

    # 更新下载记录
    updater.update_chapter_record(
        task['site'], task['comic_id'], chapter_title
    )

    log.info(f"{task['name']} {chapter_title} cbz打包完成")
    return True


def download_task(task: Dict[str, Any]):
    """处理单个漫画任务的所有章节下载"""
    if not task.get('chapter_infos'):
        log.info(f"{task['name']} 没有待下载章节")
        return

    log.info(f"开始处理 {task['name']} 的 {len(task['chapter_infos'])} 个章节")

    for index, (uuid, name) in enumerate(task['chapter_infos']):
        success = download_chapter(task, uuid, name, index)
        if not success:
            log.error(f"章节下载失败: {task['name']} {name}, CID: {uuid}")
        time.sleep(3)

    log.info(f"{task['name']} 需要更新的下载已完成")


def download_batch(tasks: List[Dict[str, Any]]):
    """批量处理多个下载任务"""
    if not tasks:
        log.info("当前没有需要更新的内容")
        return

    log.info(f"检测到 {len(tasks)} 个漫画有更新内容")

    for task in tasks:
        debug_uuids = "\n".join([f"  - {uuid} ({name})" for uuid, name in task.get('chapter_infos', [])])

        debug = (
            f"漫画名称: {task['name']}\n"
            f"漫画ID: {task['comic_id']}\n"
            f"当前章节: {task['latest_chapter']}\n"
            f"待更新数: {len(task.get('chapter_infos', []))}\n"
            f"列表:\n{debug_uuids}"
        )
        info = (
            f"漫画名称: {task['name']}\n"
            f"当前章节: {task['latest_chapter'] or '无'}\n"
            f"待更新数: {len(task.get('chapter_infos', []))}"
        )
        log.info(info)
        log.debug(debug)

        download_task(task)

    log.info("所有漫画下载任务已完成")

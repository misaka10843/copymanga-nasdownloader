import logging
import os
import time
from typing import List, Dict, Any

from downloader import downloader, postprocess
from plugins.copymanga.headers import HEADERS
from updater import updater
from utils import config
from utils.rename import rename_series
from utils.request import RequestHandler

log = logging.getLogger(__name__)

request = RequestHandler(headers=HEADERS, proxy=config.CM_PROXY)


def get_chapter(path_word: str, uuid: str):
    """获取章节详情"""
    data = request.get(f"/api/v3/comic/{path_word}/chapter2/{uuid}")
    try:
        return data.json()['results']['chapter']
    except Exception as e:
        log.error(f"漫画章节内容解析失败：{e}")
        return None


def download_chapter(task: Dict[str, Any], uuid: str, chapter_name: str):
    """下载单个章节"""
    chapter = get_chapter(task['path_word'], uuid)
    if not chapter:
        log.error(f"无法获取章节 {chapter_name} (UUID: {uuid}) 的内容")
        return False

    current_name = chapter_name
    log.info(f"已获取到 {task['name']} {current_name} 的内容，开始安排下载")

    save_path = os.path.join(config.DOWNLOAD_PATH, task['name'], current_name)
    os.makedirs(save_path, exist_ok=True)

    # 下载所有图片
    for index, url in enumerate(chapter['contents']):
        image_path = os.path.join(save_path, f"{chapter['words'][index]:04d}.jpg")
        full_url = url['url'].replace("c800x.jpg", "c1500x.jpg").replace("c800x.webp", "c1500x.webp")

        if downloader(full_url, image_path):
            log.info(f"已下载 {task['name']} {current_name} {chapter['words'][index]:04d}.jpg")
        else:
            log.error(f"下载失败: {task['name']} {current_name} {chapter['words'][index]:04d}.jpg")

    log.info(f"{task['name']} {current_name} 下载完成，开始进行cbz打包")

    # 文件重命名处理
    if not config.USE_CM_CNAME:
        chapter_filename, chapter_num, is_special = rename_series(
            current_name, task['ep_pattern'], task['vol_pattern'])
    else:
        chapter_filename, chapter_num, is_special = current_name, 0, False

    postprocess(
        task['name'], current_name,
        chapter_filename, chapter_num, save_path, is_special
    )

    # 更新下载记录
    updater.update_chapter_record(
        task['site'], task['path_word'], current_name
    )

    log.info(f"{task['name']} {current_name} cbz打包完成")
    return True


def download_task(task: Dict[str, Any]):
    """处理单个漫画任务的所有章节下载"""
    if not task.get('chapter_infos'):
        log.info(f"{task['name']} 没有待下载章节")
        return

    log.info(f"开始处理 {task['name']} 的 {len(task['chapter_infos'])} 个章节")

    for uuid, name in task['chapter_infos']:
        success = download_chapter(task, uuid, name)
        if not success:
            log.error(f"章节下载失败: {task['name']} {name}, UUID: {uuid}")
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
            f"路径标识: {task['path_word']}\n"
            f"当前章节: {task['current_chapter']}\n"
            f"待更新数: {len(task.get('chapter_infos', []))}\n"
            f"UUID列表:\n{debug_uuids}"
        )
        # 打印任务信息
        info = (
            f"漫画名称: {task['name']}\n"
            f"当前章节: {task['current_chapter'] or '无'}\n"
            f"待更新数: {len(task.get('chapter_infos', []))}"
        )
        log.info(info)
        log.debug(debug)

        # 开始下载该漫画
        download_task(task)

    log.info("所有漫画下载任务已完成")

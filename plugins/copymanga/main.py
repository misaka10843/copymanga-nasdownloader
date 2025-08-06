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


def download_chapter(task: Dict[str, Any], uuid: str):
    """下载单个章节"""
    chapter = get_chapter(task['path_word'], uuid)
    if not chapter:
        log.error(f"无法获取章节 {uuid} 的内容")
        return False

    log.info(f"已获取到{task['name']} {chapter['name']}的内容，开始安排下载")
    save_path = os.path.join(config.DOWNLOAD_PATH, task['name'], chapter['name'])
    os.makedirs(save_path, exist_ok=True)

    # 下载所有图片
    for index, url in enumerate(chapter['contents']):
        image_path = os.path.join(save_path, f"{chapter['words'][index]:04d}.jpg")
        full_url = url['url'].replace("c800x.jpg", "c1500x.jpg").replace("c800x.webp", "c1500x.webp")

        if downloader(full_url, image_path):
            log.info(f"已下载 {task['name']} {chapter['name']} {chapter['words'][index]:04d}.jpg")
        else:
            log.error(f"下载失败: {task['name']} {chapter['name']} {chapter['words'][index]:04d}.jpg")

    log.info(f"{task['name']} {chapter['name']} 下载完成，开始进行cbz打包")

    # 文件重命名处理
    if not config.USE_CM_CNAME:
        chapter_filename, chapter_num, is_special = rename_series(
            chapter['name'], task['ep_pattern'], task['vol_pattern'])
    else:
        chapter_filename, chapter_num, is_special = chapter['name'], 0, False

    postprocess(
        task['name'], chapter['name'],
        chapter_filename, chapter_num, save_path, is_special
    )

    # 更新下载记录
    updater.update_chapter_record(
        task['site'], task['path_word'], chapter['name']
    )

    log.info(f"{task['name']} {chapter['name']} cbz打包完成")
    return True


def download_task(task: Dict[str, Any]):
    """处理单个漫画任务的所有章节下载"""
    if not task['uuids']:
        log.info(f"{task['name']} 没有待下载章节")
        return

    log.info(f"开始处理 {task['name']} 的 {len(task['uuids'])} 个章节")

    for uuid in task['uuids']:
        success = download_chapter(task, uuid)
        if not success:
            log.error(f"章节下载失败: {task['name']}, UUID: {uuid}")
        time.sleep(3)

    log.info(f"{task['name']} 需要更新的下载已完成")


def download_batch(tasks: List[Dict[str, Any]]):
    """批量处理多个下载任务"""
    if not tasks:
        log.info("当前没有需要更新的内容")
        return

    log.info(f"检测到 {len(tasks)} 个漫画有更新内容")

    for task in tasks:
        debug = (
                f"漫画名称: {task['name']}\n"
                f"路径标识: {task['path_word']}\n"
                f"当前章节: {task['current_chapter']}\n"
                f"待更新数: {len(task['uuids'])}\n"
                f"UUID列表:\n" + "\n".join([f"  - {uuid}" for uuid in task['uuids']])
        )
        # 打印任务信息
        info = (
            f"漫画名称: {task['name']}\n"
            f"当前章节: {task['current_chapter'] or '无'}\n"
            f"待更新数: {len(task['uuids'])}"
        )
        log.info(info)
        log.debug(debug)

        # 开始下载该漫画
        download_task(task)

    log.info("所有漫画下载任务已完成")

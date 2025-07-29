import logging
import os
import time

import updater
from downloader import downloader, postprocess
from utils import config, request
from utils.rename import rename_series

log = logging.getLogger(__name__)
def get_chapter(path_word: str, uuid: str):
    data = request.get(f"/api/v3/comic/{path_word}/chapter2/{uuid}")
    try:
        return data.json()['results']['chapter']
    except Exception as e:
        log.error(f"漫画章节内容解析失败：{e}")

def copymanga_downloader(comic):
    for uuid in comic['uuids']:
        chapter = get_chapter(comic['path_word'], uuid)
        log.info(f"已获取到{comic['name']} {chapter['name']}的内容，开始安排下载")
        save_path = str(os.path.join(config.DOWNLOAD_PATH, comic['name'], chapter['name']))

        for index, url in enumerate(chapter['contents']):
            os.makedirs(save_path, exist_ok=True)

            image_path = str(os.path.join(save_path, f"{chapter['words'][index]:04d}.jpg"))

            url = url['url'].replace("c800x.jpg", "c1500x.jpg")

            downloader(url, image_path)
            log.info(f"已下载 {comic['name']} {chapter['name']} {chapter['words'][index]:04d}.jpg")

        log.info(f"{comic['name']} {chapter['name']} 下载完成，开始进行cbz打包")

        if not config.USE_CM_CNAME:
            chapter_filename, chapter_num, is_special = rename_series(chapter['name'], comic['ep_pattern'],
                                                                      comic['vol_pattern'])
        else:
            chapter_filename, chapter_num, is_special = chapter['name'], 0, False

        postprocess(comic['name'], chapter['name'], chapter_filename, chapter_num, save_path, is_special)
        updater.update_chapter_record(comic['path_word'], chapter['name'])
        log.info(f"{comic['name']} {chapter['name']} cbz打包完成，等待三秒继续")
        time.sleep(3)
    log.info(f"{comic['name']} 需要更新的下载已完成")
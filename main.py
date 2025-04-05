import logging
import os.path
import time

import updater
from downloader import downloader, postprocess
from utils import request, config
from utils.log import configure_logging
from utils.rename import rename_series

configure_logging()

log = logging.getLogger(__name__)


def get_chapter(path_word: str, uuid: str):
    data = request.get(f"/api/v3/comic/{path_word}/chapter2/{uuid}")
    try:
        return data.json()['results']['chapter']
    except Exception as e:
        log.error(f"漫画章节内容解析失败：{e}")


def main():
    download_list = updater.process_updates()

    if not download_list:
        log.info("当前没有需要更新的内容")
        return

    log.info(f"检测到{len(download_list)}个漫画有更新内容")
    for comic in download_list:
        debug = (
                f"漫画名称: {comic['name']}\n"
                f"路径标识: {comic['path_word']}\n"
                f"当前章节: {comic['current_chapter']}\n"
                f"待更新数: {len(comic['uuids'])}\n"
                f"UUID列表:\n" + "\n".join([f"  - {uuid}" for uuid in comic['uuids']])
        )
        info = (
            f"漫画名称: {comic['name']}\n"
            f"当前章节: {comic['current_chapter'] or '无'}\n"
            f"待更新数: {len(comic['uuids'])}"
        )
        log.debug(debug)
        log.info(info)

        # 开始进行下载
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
            print(comic)
            chapter_filename, chapter_num, is_special = rename_series(chapter['name'], comic['ep_pattern'],
                                                                      comic['vol_pattern'])
            postprocess(comic['name'], chapter['name'], chapter_filename, chapter_num, save_path, is_special)
            updater.update_chapter_record(comic['path_word'], chapter['name'])
            log.info(f"{comic['name']} {chapter['name']} cbz打包完成，等待三秒继续")
            time.sleep(3)


if __name__ == '__main__':
    main()

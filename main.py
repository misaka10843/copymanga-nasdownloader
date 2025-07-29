import logging

import updater
from plugins.copymanga.main import copymanga_downloader
from utils import request
from utils.log import configure_logging

configure_logging()

log = logging.getLogger(__name__)

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
        copymanga_downloader(comic)
    log.info(f"需要更新的所有漫画下载已完成")


if __name__ == '__main__':
    main()

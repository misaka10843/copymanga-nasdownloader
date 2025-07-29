import logging

from dispatcher import DownloadDispatcher
from updater import updater
from utils.log import configure_logging

configure_logging()

log = logging.getLogger(__name__)


def main():
    # 获取所有需要下载的任务
    all_tasks = updater.process_updates()

    if not all_tasks:
        log.info("没有发现需要下载的更新")
        return

    log.info(f"发现来自 {len(set(t['site'] for t in all_tasks))} 个站点的更新任务")

    DownloadDispatcher.download_site(all_tasks)


if __name__ == '__main__':
    main()

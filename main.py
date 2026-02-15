import logging
import traceback

from dispatcher import DownloadDispatcher
from updater import updater
from utils import config
from utils.log import configure_logging
from utils.notify import notifier

configure_logging()

log = logging.getLogger(__name__)


def main():
    config.reload()
    notifier.clear()

    try:
        all_tasks = updater.process_updates()

        if not all_tasks:
            log.info("没有发现需要下载的更新")
            notifier.flush()
            return

        log.info(f"发现来自 {len(set(t['site'] for t in all_tasks))} 个站点的更新任务")

        DownloadDispatcher.download_site(all_tasks)

    except Exception as e:
        log.error(f"主程序运行出错: {e}")
        log.debug(traceback.format_exc())
        notifier.add_error("System", "Main Loop", str(e))

    finally:
        notifier.flush()


if __name__ == '__main__':
    main()

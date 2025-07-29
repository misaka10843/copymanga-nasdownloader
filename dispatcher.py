import logging
import importlib
from typing import Dict, List, Any

log = logging.getLogger(__name__)


class DownloadDispatcher:
    SITE_MODULES = {
        "copymanga": "plugins.copymanga.main"
    }

    @classmethod
    def download_site(cls, tasks: List[Dict[str, Any]]):
        """下载指定站点的任务"""
        site_tasks = {}

        for task in tasks:
            site = task['site']
            if site not in site_tasks:
                site_tasks[site] = []
            site_tasks[site].append(task)

        for site, tasks in site_tasks.items():
            if site in cls.SITE_MODULES:
                module_path = cls.SITE_MODULES[site]
                try:
                    module = importlib.import_module(module_path)
                    log.info(f"开始处理 {site} 的 {len(tasks)} 个下载任务")

                    module.download_batch(tasks)

                    log.info(f"{site} 的所有任务处理完成")
                except ImportError:
                    log.error(f"找不到 {site} 站点的下载器")
                except Exception as e:
                    log.error(f"处理 {site} 下载任务时出错: {e}")
            else:
                log.error(f"未知站点: {site}, 无法处理下载任务")
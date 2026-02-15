import json
import logging
from pathlib import Path
from typing import Dict, List, Any

from utils import config
from utils.notify import notifier
from . import copymanga, terra_historicus, antbyw, ganganonline

log = logging.getLogger(__name__)

# 站点映射
SITE_MAPPING = {
    "copymanga": copymanga.CopyMangaUpdater,
    "terra_historicus": terra_historicus.TerraHistoricusUpdater,
    "antbyw": antbyw.AntbywUpdater,
    "ganganonline": ganganonline.GanganOnlineUpdater,
}


def load_updater_json(file_path: str = "updater.json") -> Dict[str, List[Dict]]:
    path = Path(config.DATA_PATH, file_path)
    if not path.exists():
        return {}

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # 验证数据结构
            for site, records in data.items():
                site_class = SITE_MAPPING.get(site)
                if not site_class:
                    continue

                for record in records:
                    if not site_class.validate_record(record):
                        raise ValueError(f"站点 {site} 的记录结构错误")

            return data
    except Exception as e:
        log.error(f"加载updater.json出错: {e}")
        return {}


def process_updates() -> List[Dict[str, Any]]:
    tasks = []
    site_data = load_updater_json()

    for site_name, records in site_data.items():
        site_class = SITE_MAPPING.get(site_name)
        if not site_class:
            log.error(f"未知站点: {site_name}")
            continue

        site_instance = site_class()

        for record in records:
            try:
                chapters = site_instance.get_chapters(record)
                uuids = site_instance.find_subsequent_uuids(chapters, record['latest_chapter'])

                if uuids:
                    notifier.add_update(site_name, record.get('name', '未知漫画'))
                    tasks.append(site_instance.create_download_task(record, uuids))

            except Exception as e:
                err_msg = f"处理站点 {site_name} 记录失败: {e}"
                log.error(err_msg)
                notifier.add_error(site_name, record.get('name', '更新检查'), str(e))

    return tasks


def update_chapter_record(site_name: str, comic_id: str, new_chapter: str, file_path: str = "updater.json") -> bool:
    site_data = load_updater_json(file_path)

    # 获取该站点的记录列表
    site_records = site_data.get(site_name, [])
    site_class = SITE_MAPPING.get(site_name)

    if not site_class:
        log.error(f"未知站点: {site_name}")
        return False

    site_instance = site_class()
    updated = False

    for i, record in enumerate(site_records):
        record_id = site_instance.get_unique_id(record)

        if record_id == comic_id:
            site_records[i] = site_instance.update_record(record, new_chapter)
            updated = True
            break

    if not updated:
        log.error(f"找不到站点 {site_name} 中ID为 {comic_id} 的记录")
        return False

    # 更新整个站点数据
    site_data[site_name] = site_records

    # 写回文件
    try:
        with open(Path(config.DATA_PATH, file_path), 'w', encoding='utf-8') as f:
            json.dump(site_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log.error(f"更新updater.json失败: {e}")
        return False

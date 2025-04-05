import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from utils import config, request

log = logging.getLogger(__name__)


def get_comic(path_word: str, group_word: str = "default") -> Any | None:
    log.info(f"开始获取漫画：{path_word}，类别：{group_word}")
    data = request.get(f"/api/v3/comic/{path_word}/group/{group_word}/chapters?limit=500&offset=0&platform=1")
    try:
        return data.json()['results']['list']
    except Exception as e:
        log.error(f"漫画章节列表解析失败：{e}")


def load_updater_json(file_path: str = "updater.json") -> List[Dict[str, Any]]:
    path = Path(config.DATA_PATH, file_path)
    if not path.exists():
        raise FileNotFoundError(f"无法获取到此路径下的updater.json: {path.absolute()}")

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # 验证数据结构
            for item in data:
                if not all(key in item for key in
                           ['name', 'path_word', 'group_word', 'latest_chapter', 'last_download_date']):
                    raise ValueError("updater.json结构错误")

            return data
    except json.JSONDecodeError:
        raise ValueError("updater.json的格式错误导致无法解析")


def find_subsequent_uuids(comic_data: Dict[str, Any], target_chapter: str) -> List[str]:
    chapters = sorted(comic_data, key=lambda x: x['index'])

    # 寻找目标章节位置
    target_index = -1
    for i, chapter in enumerate(chapters):
        if chapter['name'] == target_chapter:
            target_index = i
            break

    if target_index == -1 and target_chapter:
        return []

    # 检查是否是最后一个章节
    if target_index == len(chapters) - 1:
        return []

    return [chap['uuid'] for chap in chapters[target_index + 1:]]


def process_updates() -> List[Dict[str, Any]]:
    try:
        records = load_updater_json()
    except Exception as e:
        log.error(f"加载updater.json出错: {e}")
        exit(1)

    result = []

    for record in records:
        try:
            chapters = get_comic(
                path_word=record['path_word'],
                group_word=record['group_word']
            )
            uuids = find_subsequent_uuids(chapters, record['latest_chapter'])

            if uuids:
                result.append({
                    "path_word": record['path_word'],
                    "name": record['name'],
                    "uuids": uuids,
                    "group_word": record['group_word'],
                    "current_chapter": record['latest_chapter'],
                    "ep_pattern": record['ep_pattern'],
                    "vol_pattern": record['vol_pattern'],
                })

        except Exception as e:
            log.error(f"无法处理 {record['name']}: {e}")

    return result


def update_chapter_record(path_word: str, new_chapter: str, file_path: str = "updater.json") -> bool:
    try:
        # 读取全部数据
        records = load_updater_json(file_path)

        # 查找目标记录
        updated = False
        for record in records:
            if record['path_word'] == path_word:
                record['latest_chapter'] = new_chapter
                record['last_download_date'] = datetime.now().isoformat()
                updated = True
                break

        if not updated:
            log.error(f"无法在updater.json中找到 {path_word}")
            exit(1)

        # 写回文件
        with open(Path(config.DATA_PATH, file_path), 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        return True

    except Exception as e:
        log.error(f"无法更新updater.json: {e}")
        exit(1)

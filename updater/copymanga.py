import logging
from typing import Dict, List, Any

from utils import request
from .base import BaseUpdater

log = logging.getLogger(__name__)


class CopyMangaUpdater(BaseUpdater):
    SITE_NAME = "copymanga"
    ID_FIELD = "path_word"  # 唯一标识符字段
    REQUIRED_FIELDS = BaseUpdater.REQUIRED_FIELDS + [
        'name', 'path_word', 'group_word', 'ep_pattern', 'vol_pattern'
    ]

    def get_chapters(self, record: Dict) -> List[Dict]:
        log.info(f"获取漫画：{record['path_word']}，类别：{record['group_word']}")
        url = f"/api/v3/comic/{record['path_word']}/group/{record['group_word']}/chapters?limit=500&offset=0&platform=3&in_mainland=false"
        data = request.get(url)
        return data.json()['results']['list']

    def find_subsequent_uuids(self, chapters: List[Dict], target_chapter: str) -> List[str]:
        sorted_chapters = sorted(chapters, key=lambda x: x['index'])

        target_index = -1
        for i, chapter in enumerate(sorted_chapters):
            if chapter['name'] == target_chapter:
                target_index = i
                break

        if target_index == -1 or target_index == len(sorted_chapters) - 1:
            return []

        return [chap['uuid'] for chap in sorted_chapters[target_index + 1:]]

    def create_download_task(self, record: Dict, uuids: List[str]) -> Dict[str, Any]:
        return {
            "site": self.SITE_NAME,
            "path_word": record['path_word'],
            "name": record['name'],
            "uuids": uuids,
            "group_word": record['group_word'],
            "current_chapter": record['latest_chapter'],
            "ep_pattern": record['ep_pattern'],
            "vol_pattern": record['vol_pattern'],
        }

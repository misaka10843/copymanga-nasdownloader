from typing import Dict, List, Any

from .base import BaseUpdater


class TerraHistoricusUpdater(BaseUpdater):
    SITE_NAME = "terra_historicus"
    ID_FIELD = "comic_id"

    REQUIRED_FIELDS = BaseUpdater.REQUIRED_FIELDS + [
        'name'
    ]

    def get_chapters(self, record: Dict) -> List[Dict]:
        return []

    def find_subsequent_uuids(self, chapters: List[Dict], target_chapter: str) -> List[str]:
        return []

    def create_download_task(self, record: Dict, uuids: List[str]) -> Dict[str, Any]:
        return {
        }
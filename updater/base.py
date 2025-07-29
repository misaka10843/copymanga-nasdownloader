import logging
from datetime import datetime
from typing import Dict, List, Any

log = logging.getLogger(__name__)


class BaseUpdater:
    SITE_NAME = "base"
    ID_FIELD = ""
    REQUIRED_FIELDS = ['last_download_date', 'latest_chapter']

    @classmethod
    def validate_record(cls, record: Dict) -> bool:
        """验证记录是否符合站点要求"""
        if not cls.ID_FIELD:
            raise ValueError(f"{cls.SITE_NAME}站点未定义ID_FIELD")
        return all(field in record for field in [cls.ID_FIELD] + cls.REQUIRED_FIELDS)

    def get_unique_id(self, record: Dict) -> str:
        """获取记录的唯一标识符"""
        if not self.ID_FIELD:
            raise ValueError(f"{self.SITE_NAME}站点未定义ID_FIELD")
        return record.get(self.ID_FIELD, "")

    def get_chapters(self, record: Dict) -> List[Dict]:
        """获取漫画章节列表"""
        raise NotImplementedError

    def find_subsequent_uuids(self, chapters: List[Dict], target_chapter: str) -> List[str]:
        """查找后续章节UUID """
        raise NotImplementedError

    def create_download_task(self, record: Dict, uuids: List[str]) -> Dict[str, Any]:
        """创建下载任务"""
        raise NotImplementedError

    def update_record(self, record: Dict, new_chapter: str) -> Dict:
        """更新记录"""
        updated = record.copy()
        updated['latest_chapter'] = new_chapter
        updated['last_download_date'] = datetime.now().isoformat()
        return updated

import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple

log = logging.getLogger(__name__)


class BaseUpdater:
    SITE_NAME = "base"
    ID_FIELD = ""
    REQUIRED_FIELDS = ['last_download_date', 'latest_chapter']

    @classmethod
    def get_field_meta(cls) -> Dict[str, Dict[str, str]]:
        meta = {}
        # 默认字段配置
        defaults = {
            'name': {'label': '漫画名称', 'type': 'text', 'placeholder': '请输入文件夹名称', 'cols': 6},
            'comic_id': {'label': '漫画ID', 'type': 'text', 'placeholder': 'Site ID', 'cols': 6},
            'path_word': {'label': '路径词 (path_word)', 'type': 'text', 'cols': 6},
            'group_word': {'label': '汉化组/分类', 'type': 'text', 'default': 'default', 'cols': 6},
            'latest_chapter': {'label': '最后章节', 'type': 'text', 'placeholder': '留空下载所有', 'advanced': True,
                               'cols': 12},
            'last_download_date': {'label': '更新时间', 'type': 'readonly', 'advanced': True, 'cols': 12},
            'ep_pattern': {'label': '话数正则', 'type': 'text', 'advanced': True, 'cols': 6},
            'vol_pattern': {'label': '卷数正则', 'type': 'text', 'advanced': True, 'cols': 6},
        }

        if cls.ID_FIELD:
            if cls.ID_FIELD in defaults:
                meta[cls.ID_FIELD] = defaults[cls.ID_FIELD].copy()
            else:
                meta[cls.ID_FIELD] = {'label': cls.ID_FIELD, 'type': 'text', 'cols': 6}
            meta[cls.ID_FIELD]['required'] = True
            meta[cls.ID_FIELD]['primary'] = True

        for field in cls.REQUIRED_FIELDS:
            if field == cls.ID_FIELD: continue  # 跳过已处理的

            if field in defaults:
                meta[field] = defaults[field]
            else:
                meta[field] = {'label': field, 'type': 'text', 'cols': 12}

        return meta

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

    def find_subsequent_uuids(self, chapters: List[Dict], target_chapter: str) -> List[Tuple[str, str]]:
        """查找后续章节UUID和名称 (uuid, name)"""
        raise NotImplementedError

    def create_download_task(self, record: Dict, chapter_infos: List[Tuple[str, str]]) -> Dict[str, Any]:
        """创建下载任务"""
        raise NotImplementedError

    def update_record(self, record: Dict, new_chapter: str) -> Dict:
        """更新记录"""
        updated = record.copy()
        updated['latest_chapter'] = new_chapter
        updated['last_download_date'] = datetime.now().isoformat()
        return updated

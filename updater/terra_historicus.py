import logging
from typing import Dict, List, Any

from utils.request import RequestHandler
from .base import BaseUpdater

request = RequestHandler()

log = logging.getLogger(__name__)


class TerraHistoricusUpdater(BaseUpdater):
    SITE_NAME = "terra_historicus"
    ID_FIELD = "comic_id"

    REQUIRED_FIELDS = BaseUpdater.REQUIRED_FIELDS + [
        'name'  # 必须字段：漫画名称
    ]

    def get_chapters(self, record: Dict) -> List[Dict]:
        """获取漫画所有章节数据"""
        comic_id = record['comic_id']
        url = f"https://terra-historicus.hypergryph.com/api/comic/{comic_id}"

        try:
            response = request.get(url)
            data = response.json()

            if data['code'] != 0 or 'data' not in data:
                log.error(f"获取漫画章节失败: {data.get('msg', '未知错误')}")
                return []

            chapters = []
            # 提取章节数据并添加排序索引
            for idx, chapter in enumerate(data['data']['episodes']):
                chapter['index'] = idx  # 添加章节序号用于排序
                chapters.append(chapter)
            log.debug(f"章节ID: {chapters[::-1]}")
            return chapters[::-1]

        except Exception as e:
            log.exception(f"获取章节异常: {str(e)}")
            return []

    def find_subsequent_uuids(self, chapters: List[Dict], target_chapter: str) -> List[str]:
        """查找目标章节后的所有章节ID"""
        if not chapters:
            return []

        if not target_chapter:
            return [chap['cid'] for chap in chapters]

        target_index = -1
        for i, chapter in enumerate(chapters):
            if chapter['title'] == target_chapter or chapter['shortTitle'] == target_chapter:
                target_index = i
                break

        if target_index != -1 and target_index < len(chapters) - 1:
            return [chap['cid'] for chap in chapters[target_index + 1:]]

        return []

    def create_download_task(self, record: Dict, uuids: List[str]) -> Dict[str, Any]:
        """创建下载任务数据结构"""
        # 计算起始索引
        starting_index = 0
        if record.get('latest_chapter'):
            # 查找最新章节的索引
            chapters = self.get_chapters(record)
            for chapter in chapters:
                if chapter['title'] == record['latest_chapter'] or chapter['shortTitle'] == record['latest_chapter']:
                    starting_index = chapter['index']
                    break

        return {
            "site": self.SITE_NAME,
            "comic_id": record['comic_id'],
            "name": record['name'],
            "cids": uuids,
            "latest_chapter": record.get('latest_chapter', ""),
            "starting_index": starting_index
        }

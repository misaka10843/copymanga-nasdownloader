import json
import logging
from typing import Dict, List, Any, Tuple

from bs4 import BeautifulSoup

from utils.request import RequestHandler
from .base import BaseUpdater

request = RequestHandler()
log = logging.getLogger(__name__)


class GanganOnlineUpdater(BaseUpdater):
    SITE_NAME = "ganganonline"
    ID_FIELD = "comic_id"

    REQUIRED_FIELDS = BaseUpdater.REQUIRED_FIELDS + [
        'name'
    ]

    def get_chapters(self, record: Dict) -> List[Dict]:
        comic_id = record['comic_id']
        url = f"https://www.ganganonline.com/title/{comic_id}"

        try:
            response = request.get(url)

            soup = BeautifulSoup(response.text, 'html.parser')
            script_tag = soup.find("script", {"id": "__NEXT_DATA__"})

            if not script_tag:
                log.error(f"无法找到 __NEXT_DATA__ 数据: {record['name']}")
                return []

            data = json.loads(script_tag.string)

            raw_chapters = data['props']['pageProps']['data']['default'].get('chapters', [])

            chapters = []
            for ch in raw_chapters:
                # 过滤掉未发布的预告
                if ch.get('status') == 3:
                    continue

                c_id = str(ch.get('id'))
                main_text = ch.get('mainText', '')
                sub_text = ch.get('subText', '')
                full_title = f"{main_text} {sub_text}".strip()

                chapters.append({
                    "uuid": c_id,
                    "title": full_title,
                    "original_status": ch.get('status')
                })

            chapters.reverse()

            log.debug(f"获取到章节列表: {[c['title'] for c in chapters]}")
            return chapters

        except Exception as e:
            log.exception(f"获取 GanganOnline 章节异常: {str(e)}")
            return []

    def find_subsequent_uuids(self, chapters: List[Dict], target_chapter: str) -> List[Tuple[str, str]]:
        if not chapters:
            return []

        if not target_chapter:
            return [(chap['uuid'], chap['title']) for chap in chapters]

        target_index = -1
        for i, chapter in enumerate(chapters):
            if chapter['title'] == target_chapter:
                target_index = i
                break

        if target_index != -1 and target_index < len(chapters) - 1:
            return [(chap['uuid'], chap['title']) for chap in chapters[target_index + 1:]]

        if target_index == -1:
            log.warning(f"未找到上次下载的章节 '{target_chapter}'，可能是标题变更。")

        return []

    def create_download_task(self, record: Dict, chapter_infos: List[Tuple[str, str]]) -> Dict[str, Any]:
        starting_index = 0
        if record.get('latest_chapter'):
            chapters = self.get_chapters(record)
            for chapter in chapters:
                if chapter['title'] == record['latest_chapter']:
                    starting_index += 1
                    break
                starting_index += 1

        return {
            "site": self.SITE_NAME,
            "comic_id": record['comic_id'],
            "name": record['name'],
            "chapter_infos": chapter_infos,
            "latest_chapter": record.get('latest_chapter', ""),
            "starting_index": starting_index
        }

import logging
import re
from typing import Dict, List, Any, Tuple
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup, Tag

from utils.request import RequestHandler
from .base import BaseUpdater

log = logging.getLogger(__name__)
request = RequestHandler()


class AntbywUpdater(BaseUpdater):
    SITE_NAME = "antbyw"
    ID_FIELD = "comic_id"
    REQUIRED_FIELDS = BaseUpdater.REQUIRED_FIELDS + [
        'name', 'group_word'
    ]

    TYPE_MAPPING = {
        "juan": "单行本",
        "hua": "单话",
        "fanwai": "番外篇"
    }

    def get_chapters(self, record: Dict) -> List[Dict]:
        comic_id = record['comic_id']
        url = f"https://www.antbyw.com/plugin.php?id=jameson_manhua&c=index&a=bofang&kuid={comic_id}"

        domain = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Referer": domain,
        }

        log.info(f"获取漫画页面: {record['name']} (ID: {comic_id})")
        # 临时更新 headers
        request.session.headers.update(headers)
        response = request.get(url)

        if not response:
            log.error("无法获取漫画页面")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        target_type = self.TYPE_MAPPING.get(record.get('group_word'), "单话")

        target_switcher = None
        headers = soup.select("h3.uk-alert-warning")

        for header in headers:
            if target_type in header.get_text():
                log.debug(f"找到分类标题: {header}")

                curr = header.next_sibling
                sibling_count = 0
                while curr:
                    if not isinstance(curr, Tag):
                        curr = curr.next_sibling
                        continue

                    sibling_count += 1
                    classes = curr.get('class', [])
                    if (curr.name in ['ul', 'div'] and
                            ('uk-switcher' in classes or 'uk-switcher' in str(classes))):
                        target_switcher = curr
                        break

                    if curr.name == 'h3' and 'uk-alert-warning' in curr.get('class', []):
                        log.debug(f"遇到下一个标题 {curr.get_text()}，停止当前查找")
                        break

                    if sibling_count > 10:
                        log.debug("查找兄弟节点超过10个，尝试策略2")
                        break

                    curr = curr.next_sibling

                if not target_switcher:
                    log.debug("策略1未找到，尝试策略2: find_next")
                    candidate = header.find_next(attrs={"class": re.compile(r"uk-switcher")})
                    next_header = header.find_next("h3", class_="uk-alert-warning")

                    if candidate:
                        if next_header:
                            target_switcher = candidate
                        else:
                            target_switcher = candidate

                if target_switcher:
                    log.info(f"成功找到 '{target_type}' 的章节列表容器")
                    break

        if not target_switcher:
            log.warning(f"未找到分类 '{target_type}' 的章节列表，请检查网页结构或 group_word 配置")
            all_titles = [h.get_text(strip=True) for h in soup.select("h3.uk-alert-warning")]
            log.debug(f"页面上发现的标题: {all_titles}")
            return []

        chapters = []
        links = target_switcher.select("a.zj-container")

        for link in links:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            parsed = parse_qs(urlparse(href).query)
            zjid_list = parsed.get('zjid')

            if zjid_list:
                chapters.append({
                    'name': title,
                    'uuid': zjid_list[0],
                })

        log.info(f"解析到 {len(chapters)} 个章节")
        return chapters

    def find_subsequent_uuids(self, chapters: List[Dict], target_chapter: str) -> List[Tuple[str, str]]:
        # 提取数字进行排序
        def extract_number(text):
            match = re.search(r'(\d+\.?\d*)', text)
            return float(match.group(1)) if match else 0

        # 按章节号从小到大排序
        sorted_chapters = sorted(chapters, key=lambda x: extract_number(x['name']))

        result_chapters = []

        if not target_chapter:
            result_chapters = sorted_chapters
        else:
            target_index = -1
            for i, chapter in enumerate(sorted_chapters):
                if chapter['name'] == target_chapter:
                    target_index = i
                    break

            if target_index != -1 and target_index < len(sorted_chapters) - 1:
                result_chapters = sorted_chapters[target_index + 1:]

        # 返回 (uuid, name) 元组
        return [(chap['uuid'], chap['name']) for chap in result_chapters]

    def create_download_task(self, record: Dict, chapter_infos: List[Tuple[str, str]]) -> Dict[str, Any]:
        return {
            "site": self.SITE_NAME,
            "comic_id": record['comic_id'],
            "name": record['name'],
            "chapter_infos": chapter_infos,  # (uuid, name)
            "latest_chapter": record.get('latest_chapter', ""),
            "ep_pattern": record.get('ep_pattern', ""),
            "vol_pattern": record.get('vol_pattern', "")
        }

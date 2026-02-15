import logging
from typing import List

import requests

from utils import config

log = logging.getLogger("Notifier")


class NotificationManager:
    def __init__(self):
        self.updates: List[str] = []
        self.success: List[str] = []
        self.errors: List[str] = []
        self.has_events = False

    def clear(self):
        """重置状态，在每次任务开始前调用"""
        self.updates = []
        self.success = []
        self.errors = []
        self.has_events = False

    @classmethod
    def _send(cls, title: str, description: str, content: str):
        """底层发送逻辑"""
        if not config.PUSH_ENABLE:
            return

        server = config.PUSH_SERVER.rstrip('/')
        username = config.PUSH_USER
        token = config.PUSH_TOKEN

        if not config.PUSH_MARKDOWN:
            content = content.replace("**", "").replace("## ", "").replace("- ", "")

        try:
            if not server or not username:
                log.warning("推送配置不完整，跳过发送")
                return

            url = f"{server}/push/{username}"
            payload = {
                "title": title,
                "description": description,
                "content": content,
                "token": token
            }

            try:
                res = requests.post(url, json=payload, timeout=15)
                res.raise_for_status()
            except requests.exceptions.RequestException:
                try:
                    res = requests.post(url, json=payload, timeout=15)
                except:
                    log.error("推送请求失败，无法连接服务器")
                    return

            try:
                data = res.json()
            except:
                data = {"success": True}

            if isinstance(data, dict) and not data.get("success", True):
                log.error(f"推送失败: {data.get('message')}")
            else:
                log.info(f"消息推送成功: {title}")
        except Exception as e:
            log.error(f"推送请求异常: {e}")

    def add_update(self, site_name: str, manga_name: str):
        """记录发现更新"""
        msg = f"[{site_name}] {manga_name}"
        if msg not in self.updates:
            self.updates.append(msg)
            self.has_events = True
            log.info(f"通知中心: 发现更新 - {msg}")

        if not config.PUSH_SUMMARY_ONLY:
            self._send(
                title="发现更新",
                description=msg,
                content=f"**来源**: {site_name}\n\n**作品**: {manga_name}"
            )

    def add_success(self, site_name: str, manga_name: str, chapter_name: str):
        """记录下载成功"""
        msg = f"[{site_name}] {manga_name} - {chapter_name}"
        self.success.append(msg)
        self.has_events = True
        log.info(f"通知中心: 下载完成 - {msg}")

        if not config.PUSH_SUMMARY_ONLY:
            self._send(
                title="下载完成",
                description=f"{manga_name} - {chapter_name}",
                content=f"**来源**: {site_name}\n\n**作品**: {manga_name}\n\n**章节**: {chapter_name}"
            )

    def add_error(self, site_name: str, context: str, error_msg: str):
        """记录错误"""
        full_msg = f"[{site_name}] {context}: {error_msg}"
        self.errors.append(full_msg)
        self.has_events = True
        log.warning(f"通知中心: 记录错误 - {full_msg}")

    def flush(self):
        """任务结束时调用，发送汇总"""
        if not config.PUSH_ENABLE or not self.has_events:
            return

        # 发送所有
        if config.PUSH_SUMMARY_ONLY:
            self._send_summary_report()
        # 只补发缓冲下来的错误
        elif self.errors:
            self._send_error_report()

        self.clear()

    def _send_summary_report(self):
        title = "下载任务汇总"
        desc_list = []
        content_parts = []

        if self.updates:
            desc_list.append(f"更新 {len(self.updates)}")
            content_parts.append("## 🆕 发现更新")
            content_parts.extend([f"- {i}" for i in self.updates])
            content_parts.append("")

        if self.success:
            desc_list.append(f"下载 {len(self.success)}")
            content_parts.append("## ✅ 下载成功")
            # 限制显示数量，防止消息过长
            show_list = self.success[:20]
            content_parts.extend([f"- {i}" for i in show_list])
            if len(self.success) > 20:
                content_parts.append(f"... (共 {len(self.success)} 项)")
            content_parts.append("")

        if self.errors:
            desc_list.append(f"错误 {len(self.errors)}")
            content_parts.append("## ❌ 运行错误")
            content_parts.extend([f"- {i[:100]}" for i in self.errors])

        if not desc_list:
            description = "任务完成，无变更"
        else:
            description = "，".join(desc_list)

        self._send(title, description, "\n".join(content_parts))

    def _send_error_report(self):
        title = "运行错误报告"
        description = f"发生了 {len(self.errors)} 个错误"
        content = "## ❌ 错误列表\n\n" + "\n".join([f"- {e[:100]}" for e in self.errors])
        self._send(title, description, content)


notifier = NotificationManager()

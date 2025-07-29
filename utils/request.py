import logging
import time
from datetime import datetime

import requests

from utils import config

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "COPY/2.3.2",
    "authorization": config.TOKEN,
    "referer": "com.copymanga.app-2.3.2",
    "source": "copyApp",
    "version": "2.3.2",
    "region": "1",
    "device": "V417IR",
    "umstring": "b4c89ca4104ea9a97750314d791520ac",
    "platform": "3",
    "dt": datetime.now().strftime("%Y.%m.%d"),
    "deviceinfo": "24129PN74C-24129PN74C",
    "accept-encoding": "gzip",
    "webp": "1",
    "pseudoid": "KNJT34xmmyOB6A4a",
}


class RequestHandler:
    def __init__(self, retries=3, delay=3, timeout=10):
        """
        :param retries: 最大重试次数
        :param delay: 每次重试的间隔时间（秒）
        :param timeout: 请求超时时间（秒）
        """
        self.retries = retries
        self.delay = delay
        self.timeout = timeout
        self.api = config.API_URL.rstrip('/')  # 确保API地址没有结尾斜杠
        self.session = requests.Session()

    def _build_url(self, url: str) -> str:
        """智能构建完整URL"""
        # 如果已经是完整地址则直接使用
        if url.lower().startswith(('http://', 'https://')):
            return url
        # 拼接API地址和路径
        return f"{self.api}/{url.lstrip('/')}"

    def request(self, method, url, **kwargs):
        full_url = self._build_url(url)

        for attempt in range(1, self.retries + 1):
            try:
                self.session.headers.update(HEADERS)
                response = self.session.request(method, full_url, timeout=self.timeout, **kwargs)

                if response.status_code in (200, 201, 202):
                    return response
                if response.status_code is 210:
                    log.error(
                        f"[{method}] 请求失败 (状态码: {response.status_code})，URL: {full_url}，信息为：{response.json().get('message')}\n 对于210只能更换代理或者等待1小时后重试，我们无能为力")
                    exit(1)
                log.warning(
                    f"[{method}] 请求失败 (状态码: {response.status_code})，URL: {full_url}，尝试第 {attempt}/{self.retries} 次...")

            except requests.RequestException as e:
                log.warning(f"[{method}] 请求异常: {e}，URL: {full_url}，尝试第 {attempt}/{self.retries} 次...")

            time.sleep(self.delay)

        log.error(f"[{method}] 请求失败: 超过最大重试次数 ({self.retries})，URL: {full_url}")
        return None

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)


_default_client = RequestHandler()

get = _default_client.get
post = _default_client.post

import logging
import time

import requests

from utils import config

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
    "authorization": config.TOKEN,
    "referer": "https://mangacopy.com/"
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
        self.api = config.API_URL
        self.session = requests.Session()

    def request(self, method, url, **kwargs):
        for attempt in range(1, self.retries + 1):
            try:
                self.session.headers.update(HEADERS)
                response = self.session.request(method, self.api + url, timeout=self.timeout, **kwargs)

                if 200 <= response.status_code <= 302:
                    return response

                log.warning(
                    f"[{method}] 请求失败 (状态码: {response.status_code})，URL:{url}，尝试第 {attempt}/{self.retries} 次...")

            except requests.RequestException as e:
                log.warning(f"[{method}] 请求异常: {e}，URL:{url}，尝试第 {attempt}/{self.retries} 次...")

            time.sleep(self.delay)

        log.error(f"[{method}] 请求失败: 超过最大重试次数 ({self.retries})，URL:{url}")
        return None

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)


_default_client = RequestHandler()

get = _default_client.get
post = _default_client.post

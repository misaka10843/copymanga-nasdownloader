import json
import logging
import os

from dotenv import load_dotenv

load_dotenv(verbose=True)

log = logging.getLogger(__name__)

DATA_PATH = os.getenv("CMNAS_DATA_PATH") or os.getcwd()
SYSTEM_CONFIG_PATH = os.path.join(DATA_PATH, "system_config.json")

DOWNLOAD_PATH = ""
CBZ_PATH = ""
USE_CM_CNAME = False
LOG_LEVEL = "INFO"
CM_API_URL = ""
CM_TOKEN = ""
CM_USERNAME = ""
CM_PASSWORD = ""
CM_PROXY = {}

# Push 配置
PUSH_ENABLE = False
PUSH_SERVER = ""
PUSH_USER = ""
PUSH_TOKEN = ""
PUSH_SUMMARY_ONLY = True
PUSH_MARKDOWN = True


def load_system_config():
    """读取 system_config.json"""
    if os.path.exists(SYSTEM_CONFIG_PATH):
        try:
            with open(SYSTEM_CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log.error(f"读取系统配置失败: {e}")
    return {}


def reload():
    global DOWNLOAD_PATH, CBZ_PATH, USE_CM_CNAME, LOG_LEVEL
    global CM_API_URL, CM_TOKEN, CM_USERNAME, CM_PASSWORD, CM_PROXY
    global PUSH_ENABLE, PUSH_SERVER, PUSH_USER, PUSH_TOKEN, PUSH_SUMMARY_ONLY, PUSH_MARKDOWN

    json_conf = load_system_config()

    def get_conf(key, env_key, default):
        if key in json_conf and json_conf[key] is not None:
            if isinstance(default, bool):
                return bool(json_conf[key])
            return json_conf[key]
        return os.getenv(env_key) or default

    DOWNLOAD_PATH = get_conf("download_path", "CMNAS_DOWNLOAD_PATH", os.path.join(os.getcwd(), "downloads"))
    CBZ_PATH = get_conf("cbz_path", "CMNAS_CBZ_PATH", os.path.join(os.getcwd(), "cbz"))

    use_cm_cname_raw = get_conf("use_cm_cname", "CMNAS_USE_CM_CNAME", False)
    if isinstance(use_cm_cname_raw, str):
        USE_CM_CNAME = use_cm_cname_raw.lower() in ('true', '1', 'yes')
    else:
        USE_CM_CNAME = bool(use_cm_cname_raw)

    LOG_LEVEL = get_conf("log_level", "CMNAS_LOG_LEVEL", 'WARNING')

    # Copymanga配置
    CM_API_URL = get_conf("api_url", "CMNAS_API_URL", 'https://api.mangacopy.com')
    CM_TOKEN = get_conf("cm_token", "CMNAS_CM_TOKEN", '')
    CM_USERNAME = get_conf("cm_username", "CMNAS_CM_USERNAME", '')
    CM_PASSWORD = get_conf("cm_password", "CMNAS_CM_PASSWORD", '')

    proxy_str = get_conf("cm_proxy", "CMNAS_CM_PROXY", '')
    CM_PROXY = {'http': proxy_str, 'https': proxy_str} if proxy_str else {}

    # Push 配置
    PUSH_ENABLE = get_conf("push_enable", "PUSH_ENABLE", False)
    PUSH_SERVER = get_conf("push_server", "PUSH_SERVER", "")
    PUSH_USER = get_conf("push_user", "PUSH_USER", "")
    PUSH_TOKEN = get_conf("push_token", "PUSH_TOKEN", "")
    PUSH_SUMMARY_ONLY = get_conf("push_summary_only", "PUSH_SUMMARY_ONLY", True)
    PUSH_MARKDOWN = get_conf("push_markdown", "PUSH_MARKDOWN", True)

    log.info("配置已重新加载")


reload()

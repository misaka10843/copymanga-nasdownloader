import json
import logging
import os

from dotenv import load_dotenv

load_dotenv(verbose=True)

log = logging.getLogger(__name__)

DATA_PATH = os.getenv("CMNAS_DATA_PATH") or os.getcwd()

# 基础配置
DOWNLOAD_PATH = os.path.join(DATA_PATH, "downloads")
CBZ_PATH = os.path.join(DATA_PATH, "cbz")
USE_CM_CNAME = True
LOG_LEVEL = "INFO"

# CopyManga配置
CM_USERNAME = ""
CM_PASSWORD = ""
CM_API_URL = "https://api.mangacopy.com"
CM_PROXY = {}

# Push配置
PUSH_ENABLE = False
PUSH_SERVER = ""
PUSH_USER = ""
PUSH_TOKEN = ""
PUSH_SUMMARY_ONLY = True
PUSH_MARKDOWN = True


def reload():
    global DOWNLOAD_PATH, CBZ_PATH, USE_CM_CNAME, LOG_LEVEL
    global CM_USERNAME, CM_PASSWORD, CM_API_URL, CM_PROXY
    global PUSH_ENABLE, PUSH_SERVER, PUSH_USER, PUSH_TOKEN, PUSH_SUMMARY_ONLY, PUSH_MARKDOWN

    sys_cfg_path = os.path.join(DATA_PATH, "system_config.json")
    sys_settings = {}
    if os.path.exists(sys_cfg_path):
        try:
            with open(sys_cfg_path, 'r', encoding='utf-8') as f:
                sys_settings = json.load(f)
        except:
            pass

    # 基础配置
    DOWNLOAD_PATH = sys_settings.get('download_path') or os.getenv("CMNAS_DOWNLOAD_PATH") or os.path.join(DATA_PATH,
                                                                                                          "downloads")
    CBZ_PATH = sys_settings.get('cbz_path') or os.getenv("CMNAS_CBZ_PATH") or os.path.join(DATA_PATH, "cbz")

    use_cname_raw = sys_settings.get('use_cm_cname')
    if use_cname_raw is None:
        USE_CM_CNAME = os.getenv("CMNAS_USE_CM_CNAME", 'true').lower() == 'true'
    else:
        USE_CM_CNAME = bool(use_cname_raw)

    LOG_LEVEL = sys_settings.get('log_level') or os.getenv("CMNAS_LOG_LEVEL") or "INFO"

    # CopyManga配置
    CM_USERNAME = sys_settings.get('cm_username') or os.getenv("CM_USERNAME") or ""
    CM_PASSWORD = sys_settings.get('cm_password') or os.getenv("CM_PASSWORD") or ""
    CM_API_URL = sys_settings.get('api_url') or os.getenv("CM_API_URL") or "https://api.mangacopy.com"

    proxy_str = sys_settings.get('cm_proxy') or os.getenv("CM_PROXY")
    CM_PROXY = {'http': proxy_str, 'https': proxy_str} if proxy_str else {}

    # Push配置
    PUSH_ENABLE = sys_settings.get('push_enable', os.getenv('PUSH_ENABLE', 'false').lower() == 'true')
    PUSH_SERVER = sys_settings.get('push_server', os.getenv('PUSH_SERVER', ''))
    PUSH_USER = sys_settings.get('push_user', os.getenv('PUSH_USER', ''))
    PUSH_TOKEN = sys_settings.get('push_token', os.getenv('PUSH_TOKEN', ''))
    PUSH_SUMMARY_ONLY = sys_settings.get('push_summary_only', os.getenv('PUSH_SUMMARY_ONLY', 'true').lower() == 'true')
    PUSH_MARKDOWN = sys_settings.get('push_markdown', os.getenv('PUSH_MARKDOWN', 'true').lower() == 'true')

    log.info("配置已重新加载")


reload()

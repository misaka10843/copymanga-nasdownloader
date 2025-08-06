import os

from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv(verbose=True)
# 尝试从环境变量中获取配置值
DOWNLOAD_PATH = os.getenv("CMNAS_DOWNLOAD_PATH")
CBZ_PATH = os.getenv("CMNAS_CBZ_PATH")
DATA_PATH = os.getenv("CMNAS_DATA_PATH") or os.getcwd()
USE_CM_CNAME = os.getenv("CMNAS_USE_CM_CNAME") or False
LOG_LEVEL = os.getenv("CMNAS_LOG_LEVEL") or 'WARNING'

# copymanga设置
CM_API_URL = os.getenv("CMNAS_API_URL") or 'https://api.mangacopy.com'
CM_TOKEN = os.getenv("CMNAS_CM_TOKEN") or ''
CM_USERNAME = os.getenv("CMNAS_CM_USERNAME") or ''
CM_PASSWORD = os.getenv("CMNAS_CM_PASSWORD") or ''
proxy = os.getenv("CMNAS_CM_PROXY") or ''
CM_PROXY = proxy if {'http': proxy, 'https': proxy} else {}

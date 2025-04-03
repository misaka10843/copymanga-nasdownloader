import os

from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv(verbose=True)
# 尝试从环境变量中获取配置值
TOKEN = os.getenv("CMNAS_TOKEN") or ''
DOWNLOAD_PATH = os.getenv("CMNAS_DOWNLOAD_PATH")
CBZ_PATH = os.getenv("CMNAS_CBZ_PATH")
DATA_PATH = os.getenv("CMNAS_DATA_PATH") or os.getcwd()
USE_CM_CNAME = os.getenv("CMNAS_USE_CM_CNAME")
API_URL = os.getenv("CMNAS_API_URL")
LOG_LEVEL = os.getenv("CMNAS_LOG_LEVEL") or 'WARNING'

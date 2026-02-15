import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler

from dotenv import load_dotenv
from rich.logging import RichHandler

load_dotenv(verbose=True)


def configure_logging():
    log_level = os.getenv("CMNAS_LOG_LEVEL") or 'WARNING'
    data_path = os.getenv("CMNAS_DATA_PATH") or os.getcwd()
    log_path = os.path.join(data_path, 'log')
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    info_file_name = time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log'

    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(data_path, 'log', info_file_name),
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8',
        utc=False,
    )
    file_handler.suffix = "%Y-%m-%d.log"
    rich_handler = RichHandler(
        show_time=False,
        show_path=False,
        markup=True
    )

    file_formatter = logging.Formatter(
        fmt='%(asctime)s [%(name)s]  %(levelname)s  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    rich_formatter = logging.Formatter(
        fmt='[%(name)s] %(message)s',
        datefmt="[%X]"
    )

    file_handler.setFormatter(file_formatter)
    rich_handler.setFormatter(rich_formatter)

    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(rich_handler)

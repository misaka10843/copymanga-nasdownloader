import logging

from plugins.copymanga import updater
from plugins.copymanga.main import copymanga_downloader
from utils.log import configure_logging

configure_logging()

log = logging.getLogger(__name__)

def main():
    copymanga_downloader()


if __name__ == '__main__':
    main()

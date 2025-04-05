import logging

import updater
from utils import request
from utils.log import configure_logging

configure_logging()

log = logging.getLogger(__name__)





print(updater.process_updates())
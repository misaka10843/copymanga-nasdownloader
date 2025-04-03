import logging

from utils.log import configure_logging

configure_logging()

log = logging.getLogger(__name__)
log.debug("test")

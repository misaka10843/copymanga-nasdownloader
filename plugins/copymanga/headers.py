from datetime import datetime

from utils import config

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
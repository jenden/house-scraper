import logging
from datetime import datetime
import os
logging.basicConfig(level=logging.INFO)

LOG_DIR = os.path.join(os.path.dirname(__file__), '../logs/')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logger = logging.getLogger()
fname = datetime.now().date().isoformat() + '.log'
fh = logging.FileHandler(os.path.join(LOG_DIR, fname))
fh.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S'))
logger.addHandler(fh)

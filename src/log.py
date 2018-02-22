import logging
from datetime import datetime
import os
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()
fname = datetime.now().date().isoformat() + '.log'
fh = logging.FileHandler(os.path.join('../logs/', fname))
fh.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S'))
logger.addHandler(fh)

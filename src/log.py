import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('ParsingErrorLog')
fh = logging.FileHandler('../logs/errors.log')
fh.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S'))
logger.addHandler(fh)

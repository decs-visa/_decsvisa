"""
Logging module
"""

import logging
import platform
from pathlib import Path

# Set up logs
logger = logging.getLogger(__name__)

# Log everything / something
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

running_on = platform.platform()
if running_on.startswith("Windows"):
    file_path = Path("decs_visa.log")
    fh = logging.FileHandler(file_path)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info("OS is: %s", running_on)
else:
    # log to console (to allow PIPEd output)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.info("OS is: %s", running_on)

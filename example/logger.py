"""
Tests if the logger works and emits regularly
"""

import logging
import time

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print(logger.name)

for i in range(3):
    logger.debug("foo")
    time.sleep(1)

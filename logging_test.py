# import logging

# logging.basicConfig(level=logging.INFO)

# logger = logging.getLogger(__name__)

# logger.debug("Debug Message")
# logger.info("Info Message")
# logger.warning("Warning Message")
# logger.error("Error Message")


import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

try:
    result = 10 / 0
except Exception:
    logger.exception("Something went wrong")
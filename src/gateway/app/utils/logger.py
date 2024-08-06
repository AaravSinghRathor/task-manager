import logging
import sys

# get logger
logger = logging.getLogger()

# formatter
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(message)s"
)

# handlers
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("task-manager.log")

# set formatter
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# add handlers
logger.addHandler(stream_handler)

# set log level
logger.setLevel(logging.INFO)

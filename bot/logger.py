import logging
import sys

from common import SETTINGS

LOG_FORMAT = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")


def initialize():
    """
    Initialize the logging facilities
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Log to stdout at INFO
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(LOG_FORMAT)
    logger.addHandler(stdout_handler)

    # Log to file at DEBUG
    if SETTINGS.bot.log_file:
        file_handler = logging.FileHandler(
            filename=SETTINGS.bot.log_file, encoding="utf-8", mode="w"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(LOG_FORMAT)
        logger.addHandler(file_handler)


def get(name=""):
    """
    Get the specified logger
    :param name: the name of the logger
    :return: the logger
    """
    return logging.getLogger(f"wafflebot{'.' + name if name else ''}")

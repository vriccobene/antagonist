import os
import logging


def configure_logging():
    global logger

    DEBUG = os.getenv('DEBUG')
    if DEBUG == "True":
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
    logging.basicConfig(
        level=logging_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

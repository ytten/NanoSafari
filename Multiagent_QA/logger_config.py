import logging
import os
from datetime import datetime

def _setup_logger(log_directory, log_filename):
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_format = logging.Formatter("[%(asctime)s %(levelname)s] %(message)s")


    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(f'{log_directory}/{log_filename}')
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)


    logger.propagate = False

    return logger


current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f'_{current_time}_log.txt'

logger = _setup_logger('logger', log_filename)


if __name__ == '__main__':
    try:
        result = 1 / 0
    except Exception as e:
        logger.error("An error occurred: %s", e)
        logger.info(e, exc_info=True)
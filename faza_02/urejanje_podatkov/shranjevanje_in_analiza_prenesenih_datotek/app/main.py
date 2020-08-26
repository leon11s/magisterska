import logging

from helpers.config_reader import GENERAL_MODE
from batch import run_batch_mode
from realtime import run_realtime_mode


logger = logging.getLogger('cyberlab_files_analysis')
logger.setLevel(logging.DEBUG)

# Create handlers
cmd_handler = logging.StreamHandler()
file_handler = logging.FileHandler('./app/logs/app.log')
cmd_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.ERROR)

# Create formatters and add it to handlers
log_format = logging.Formatter('[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
cmd_handler.setFormatter(log_format)
file_handler.setFormatter(log_format)

# Add handlers to the logger
logger.addHandler(cmd_handler)
logger.addHandler(file_handler)

if __name__ == "__main__":
    if GENERAL_MODE == 'batch':
        logger.info('Running in batch mode...')
        run_batch_mode()
    elif GENERAL_MODE == 'realtime':
        pass
    else:
        logger.error('Error reading program MODE. Change MODE to batch or realtime.')
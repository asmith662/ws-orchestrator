# logger
import logging
import os
from logging.handlers import RotatingFileHandler


def logger():
    try:
        log_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../ws-orchestrator.log'))
        logging.basicConfig(
            handlers=[
                RotatingFileHandler(
                    log_path,
                    maxBytes=25000000,
                    backupCount=5
                )
            ],
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            datefmt='%d-%b-%y %H:%M:%S'
        )
        logging.info('Starting ws-orchestrator...')
        return True
    except Exception as e:
        print('While configuring logger, error:', e)
        return False

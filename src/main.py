import asyncio
import logging
import os.path
from logging.handlers import RotatingFileHandler

"""
------------------------------------------------------------------------------------------------------------------------
Acronyms List:
------------------------------------------------------------------------------------------------------------------------
    wl = word list
    fp = file path
    fn = file name
    ext = extension
------------------------------------------------------------------------------------------------------------------------
"""

# logger
log_path = os.path.realpath(os.path.join(os.path.dirname(__file__), 'ws-orchestrator.log'))
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


async def main():
    if __name__ == '__main__':
        # pwd = input(' sudo password: ')  # hard-coded password for testing
        # run_cmd('iwconfig', pwd)
        # update_interfaces()
        pass


asyncio.run(main())

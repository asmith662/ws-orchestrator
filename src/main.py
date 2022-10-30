import asyncio
import logging
import os.path
from logging.handlers import RotatingFileHandler

from src.models.cmd.cmd import run_cmd, run_cmd
from src.models.network import update_interfaces, get_interfaces
from src.models.password import can_sudo

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
        # test your commands
        # print(run_cmd(input(' enter cmd: \n'), input(' sudo password: \n')))
        # o, e = run_cmd('iwconfig', 'Af4Tf2Dp!')
        # run_cmd('iwconfig 2>&1 | grep -oP "^\\w+"', 'Af4Tf2Dp!')

        nics = get_interfaces()
        print(nics)

        # update_interfaces()


asyncio.run(main())

import asyncio
import logging
import os.path
from logging.handlers import RotatingFileHandler

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

# Arguments
DO_NOT_KILL = False


async def main():
    if __name__ == '__main__':
        # result = await run_shell_cmd('echo "Hello, world!"')
        # print(result)

        pass


asyncio.run(main())

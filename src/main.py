import asyncio
import logging
import os.path
from logging.handlers import RotatingFileHandler

from src.config import setup
from src.models.interface.ifaces import Ifaces


async def main():
    if __name__ == '__main__':
        setup()
        print(Ifaces())


asyncio.run(main())

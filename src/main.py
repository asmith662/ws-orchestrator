import asyncio
import logging
import os.path
from logging.handlers import RotatingFileHandler

from src.config import setup
from src.models.interface.iface import ifaces


async def main():
    if __name__ == '__main__':
        setup()
        interfaces = ifaces()
        for i in interfaces:
            print(i)


asyncio.run(main())

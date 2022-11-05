import asyncio
import logging
import os.path
from logging.handlers import RotatingFileHandler

from src.config import setup
from src.models.fmt import tab, msg


async def main():
    if __name__ == '__main__':
        setup()
        # auth()
        i1 = tab('this', 3)
        i2 = tab('that', 4)
        i3 = tab('something', 5)
        m = msg(i1, i2, i3)
        print(m)


asyncio.run(main())

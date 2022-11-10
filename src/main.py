import asyncio
import subprocess

from pyrcrack import AircrackNg

from src.models.network.interfaces import Interfaces
from src.models.general.users import Users
from src.models.resources.scrapy import iwconfig
from src.models.tools.doc import OptsParser


async def main():
    if __name__ == '__main__':
        # monitors, interfaces = iwconfig()
        # print(monitors)
        # print(interfaces)
        s = subprocess.check_output('aircrack-ng 2>&1; echo', shell=True).decode()
        kwargs = OptsParser(s).dict
        for k, v in kwargs.items():
            print(k, v)


asyncio.run(main())

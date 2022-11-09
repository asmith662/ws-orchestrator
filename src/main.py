import asyncio

from pyrcrack import AircrackNg

from src.models.network.interfaces import Interfaces
from src.models.general.users import Users
from src.models.resources.scrapy import iwconfig
from src.models.tools.doc import Test, OptsDoc


async def main():
    if __name__ == '__main__':
        # monitors, interfaces = iwconfig()
        # print(monitors)
        # print(interfaces)
        d = OptsDoc.data(Test.__doc__)



asyncio.run(main())

import asyncio
from src.models.network.interfaces import Interfaces
from src.models.general.users import Users
from src.models.resources.scrapy import iwconfig


async def main():
    if __name__ == '__main__':
        monitors, interfaces = iwconfig()
        print(monitors)
        print(interfaces)


asyncio.run(main())

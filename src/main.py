import asyncio

from src.config import setup
from src.models.network.interfaces import Interfaces


async def main():
    if __name__ == '__main__':
        setup()
        interfaces = Interfaces()
        # for i in interfaces:
        #     print(i)


asyncio.run(main())

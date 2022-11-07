import asyncio
from src.models.network.interfaces import Interfaces
from src.models.general.users import Users


async def main():
    if __name__ == '__main__':
        users = Users().users
        for u in users:
            print(u)

        for i in Interfaces().interfaces:
            print(i)


asyncio.run(main())

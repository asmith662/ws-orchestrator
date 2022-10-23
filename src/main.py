import asyncio
import subprocess
import pyrcrack

from src.resources.process import execute, echo, cat


async def main():
    if __name__ == '__main__':
        # airmon = pyrcrack.AirmonNg()
        # interfaces = await get_interfaces(airmon)
        # print(interfaces)
        result = await echo('hello')
        print(result)
        c = await cat('hey')
        print(c)


async def get_interfaces(airmon):
    for a in await airmon.interfaces:
        print(a)
        print(a.asdict())

    return [a.asdict() for a in await airmon.interfaces]


asyncio.run(main())

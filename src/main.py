import asyncio
import subprocess

from src.models.command.doc import Doc


async def main():
    if __name__ == '__main__':
        # monitors, interfaces = iwconfig()
        # print(monitors)
        # print(interfaces)
        s = subprocess.check_output('aircrack-ng 2>&1; echo', shell=True).decode()
        d = Doc(s).options
        for k, v in d.items():
            print(k, v)


asyncio.run(main())

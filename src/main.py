import asyncio
import logging
import os
import subprocess as sub
import tempfile

from pyrcrack import AirodumpNg
from rich.console import Console
from rich.prompt import Prompt

from src import Startup, find_user
from src.models.ng import *


async def scan_for_targets():
    """Scan for targets, return json."""
    console = Console()
    console.clear()
    console.show_cursor(False)
    amon = AirmonNg()
    ifaces = [a.interface for a in await amon.interfaces]

    interface = Prompt.ask('Select an interface', choices=ifaces)

    async with amon(interface) as mon:
        logging.info(f'Monitoring mode enabled on: [{interface}]')
        async with AirodumpNg() as pdump:
            print('here 2')
            async for result in pdump(mon.monitor_interface):
                print('here 3')
                console.clear()
                console.print(result.table)
                await asyncio.sleep(2)


async def main():
    if __name__ == '__main__':
        Startup()
        user = find_user()
        # await scan_for_targets()

        # out = None
        # with Popen(f'ls /tmp'.split(), stdout=PIPE) as proc_launch:
        #     out = proc_launch.communicate()[0].split(b'\n')
        # for line in out:
        #     print(line)

        fd, path = tempfile.mkstemp(prefix=f'{os.getlogin()}_', suffix='_key')
        with os.fdopen(fd, 'wb') as fp:
            fp.write(''.encode())

        result = sub.run(f'sudo -S rm {path}'.split(), **dict(stderr=sub.DEVNULL, input=open(path, 'r').read().encode())
                         ).returncode
        print('return code', result)


asyncio.run(main())

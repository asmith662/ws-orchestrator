import asyncio
import logging
import sys
from subprocess import Popen, PIPE, DEVNULL

from rich.console import Console
from rich.prompt import Prompt

from src.models import Startup, User, AirmonNg, AirodumpNg, secret_manager


async def scan_for_targets(path):
    """Scan for targets, return json."""
    console = Console()
    console.clear()
    console.show_cursor(False)
    with secret_manager(path) as sec:
        amon = AirmonNg(sec)
        if not (ifaces := [a.interface for a in await amon.interfaces]):
            print('\nNo usable interfaces detected...')
            if Prompt.ask('Please ensure your wireless NIC is detected by the system',
                          choices=['RETRY', 'QUIT']) == 'RETRY':
                await scan_for_targets(path)
            else:
                sys.exit()

        interface = Prompt.ask('Select an interface', choices=ifaces)

        async with amon(interface) as mon:
            logging.info(f'Monitoring mode enabled on: [{interface}]')
            async with AirodumpNg(sec) as pdump:
                print('here 2')
                async for result in pdump(mon.monitor_interface):
                    print('here 3')
                    console.clear()
                    console.print(result.table)
                    await asyncio.sleep(2)


async def main():
    if __name__ == '__main__':
        Startup()
        # print(test())
        path = User().secret_file
        # with secret_manager(path) as sec:
        #     proc = Popen(f'sudo -S iwconfig'.split(), stdout=PIPE, stderr=DEVNULL, stdin=sec)
        #     out = proc.communicate()[0].split(b'\n')
        #     for o in out:
        #         print(o)
        # user.secret_fp = ''
        # with secret_manager(user) as sec:
        #     proc = sub.Popen(f'sudo -S iwconfig'.split(), stdout=sub.PIPE, stdin=sec.read().encode())
        #     out = proc.communicate()[0].split(b'\n')
        # for o in out:
        #     print(o)
        await scan_for_targets(path)
        # read, write = os.pipe()
        # os.write(write, b"")
        # os.close(write)
        # out = sub.check_call('sudo -S echo TRUE'.split(), stdin=read, stderr=sub.DEVNULL)
        # print(out)


asyncio.run(main())

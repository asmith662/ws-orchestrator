import asyncio

from rich.console import Console
from rich.prompt import Prompt

from src.models import Startup, User, AirmonNg, AirodumpNg
from src.models.bluetooth import HciConfig


async def scan_for_targets(secret):
    """Scan for targets, return json."""
    console = Console()
    console.clear()
    console.show_cursor(False)
    airmon = AirmonNg(secret)
    interfaces = await airmon.interfaces

    # iface = [a.asdict() for a in await airmon.interfaces][0]
    interface = Prompt.ask('Select an interface',
                           choices=[str(a) for a in interfaces])
    # client = None
    # ap_ = None
    #
    # async with airmon(interface) as mon:
    #     async with AirodumpNg(secret) as pdump:
    #         # results = pdump(MONITOR.get())
    #         # while not results:
    #         #     results = pdump(MONITOR.get())
    #         #     await asyncio.sleep(2)
    #         print('here', mon.monitor_interface)
    #         async for aps in pdump(mon.monitor_interface):
    #             console.clear()
    #             # console.print(aps.table)
    #             print(aps)
    #             client = Prompt.ask(
    #                 'Select an AP',
    #                 choices=['continue', *[str(a) for a in range(len(aps))]])
    #             if client != 'continue':
    #                 ap_ = aps[int(client)]
    #                 break
    #
    #     if not ap_:
    #         return
    #
    #     async with AirodumpNg(secret) as pdump:
    #         console.print(
    #             ":vampire:",
    #             f"Selected client: [red] {ap_.bssid} [/red]")
    #
    #         async for result in pdump(MONITOR.get(), **ap_.airodump):
    #             console.clear()
    #             # console.print(result.table)
    #             print(result.table)
    #             await asyncio.sleep(3)
    # async with airmon(iface) as mon:
    #     async with AirodumpNg(secret) as pdump:
    #         async for aps in pdump(mon.monitor_interface):
    #             break
    # print(aps)
    # if not (ifaces := [a.interface for a in await airmon.interfaces]):
    #     print('\nNo usable interfaces detected...')
    #     if Prompt.ask('Please ensure your wireless NIC is detected by the system',
    #                   choices=['RETRY', 'QUIT']) == 'RETRY':
    #         await scan_for_targets(secret)
    #     else:
    #         sys.exit()
    #
    # interface = Prompt.ask('Select an interface', choices=ifaces)
    #
    async with airmon(interface) as mon:
        print(f'Monitoring mode enabled on: [{interface}]')
        async with AirodumpNg(secret) as pdump:
            print('starting airodump')
            async for result in pdump(mon.monitor_interface):
                print(result)
                console.clear()
                console.print(result.table)
                await asyncio.sleep(2)


async def main():
    if __name__ == '__main__':
        Startup()
        user = User()
        with user.secret() as sec:
            # hci = HciConfig(sec)
            # results = await hci.get_result()
            # print(results)
            await scan_for_targets(sec)


asyncio.run(main())

# with secret() as s:
#     result = run('sudo -S airmon-ng check kill'.split(), stdin=s, stderr=DEVNULL)
#     print('Killing network processes, and enabling monitoring mode')
#     iw = iw.split(b'\n') \
#         if (iw := check_output('iw dev'.split(), stdin=s, stderr=DEVNULL)) else []
#     iface = [i for i in iw if b'Interface' in i][0].decode()[11:]
#     mode = [i for i in iw if b'type' in i][0].decode()[7:]
#     print(iface, mode)
#     if iface == 'wlan0':
#         if mode == 'monitor':
#             run('sudo -S ip link set wlan0 down'.split(), stdin=s, stderr=DEVNULL)
#             run('sudo -S iw wlan0 set type managed'.split(), stdin=s, stderr=DEVNULL)
#         out = check_output('sudo -S airmon-ng start wlan0'.split(), stdin=s, stderr=DEVNULL)
#         print(out)
#     elif iface == 'wlan0mon' and mode != 'monitor':
#         out = check_output('sudo -S airmon-ng start wlan0'.split(), stdin=s, stderr=DEVNULL)
#         print(out)

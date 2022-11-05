import socket
from typing import List, Tuple, Optional

import psutil
from psutil._common import snicstats, snetio, bytes2human, snicaddr

from src.models.fmt import Fmt
from src.models.interface.iaddr import IAddr


class Iface:
    address_family_map = {
        socket.AF_INET: 'IPv4',
        socket.AF_INET6: 'IPv6',
        psutil.AF_LINK: 'MAC',
    }
    duplex_type_map = {
        psutil.NIC_DUPLEX_FULL: "full",
        psutil.NIC_DUPLEX_HALF: "half",
        psutil.NIC_DUPLEX_UNKNOWN: "?",
    }

    def __init__(self, nic: str, addrs: list[snicaddr], stats: dict[str, snicstats] = None,
                 io_counters: snetio = None):
        self.speed, self.duplex, self.mtu, self.isup, self.bytes_recv, self.bytes_sent, self.packets_recv, \
        self.packets_sent, self.errin, self.errout, self.dropin, self.dropout, self.addrs \
            = None, None, None, None, None, None, None, None, None, None, None, None, None
        self.nic = nic
        if stats:
            self.speed = stats
            self.duplex = self.set_duplex_type(stats['2'])
            self.mtu = stats['3']
            self.isup = True if stats['4'] else False
        if io_counters:
            self.bytes_recv = bytes2human(io_counters.bytes_recv)
            self.bytes_sent = bytes2human(io_counters.bytes_sent)
            self.packets_recv = io_counters.packets_recv
            self.packets_sent = io_counters.packets_sent
            self.errin = io_counters.errin
            self.errout = io_counters.errout
            self.dropin = io_counters.dropin
            self.dropout = io_counters.dropout
        if addrs:
            self.addrs = [IAddr(addr) for addr in addrs]

    def __repr__(self):
        return repr(f'Iface("{self.nic}",{self.speed},"{self.duplex}"]",{self.mtu},{self.isup},{self.bytes_recv},'
                    f'{self.bytes_sent},{self.packets_recv},{self.packets_sent},{self.errin},{self.errout},'
                    f'{self.dropin},{self.dropout},[{self.addrs}])')

    def __iter__(self):
        return self

    def __next__(self):
        if not (self.nic and self.addrs):
            raise StopIteration
        return self

    def __str__(self):
        s = 'stats' + Fmt.t(f': speed={self.speed}MB, duplex={self.duplex}, mtu={self.mtu}, up={self.isup}', 2)
        i = f'incoming' + \
            Fmt.t(f': bytes={self.bytes_recv}, pkts={self.packets_recv}, errs={self.errout}, drops={self.dropin}')
        o = f'outgoing' + \
            Fmt.t(f': bytes={self.bytes_sent}, pkts={self.packets_sent}, errs={self.errin}, drops={self.dropout}')
        for a in self.addrs:
            addr = Fmt.t(f'{self.a.family} address   : {self.address}', 1)
            broadcast = Fmt.t(f'broadcast : {self.broadcast}', 3)
            netmask = Fmt.t(f'netmask : {self.netmask}', 3)
            p2p = Fmt.t(f'p2p : {self.p2p}', 3)
        return Fmt.m(self.nic, Fmt.t(s, 1), Fmt.t(i, 1), Fmt.t(o, 1), Fmt.t(self.addrs, 1))

    @classmethod
    def set_duplex_type(cls, duplex):
        return cls.duplex_type_map[duplex]

    @classmethod
    def set_addrs_family(cls, key, val):
        return cls.address_family_map.get(key, val)

    @classmethod
    def create_addrs_dict(cls, addrs):
        for a in addrs:
            pass

    @staticmethod
    def _get() -> list[tuple[str, list[snicaddr], Optional[snicstats], Optional[snicstats]]]:
        nstats, iostats, nstat, iostat = psutil.net_if_stats(), psutil.net_io_counters(pernic=True), None, None
        nics_addrs = psutil.net_if_addrs()
        data = []
        for nic, addrs in nics_addrs.items():
            nstat = n if (n := nstats[nic]) else None
            iostat = io if (io := nstats[nic]) else None
            data.append((nic, addrs, nstat, iostat,))
        return data

    @staticmethod
    def exists(stat: dict[str, snicstats] or snetio) -> bool:
        return bool(stat)

    def refresh(self):
        for _ in self._get():
            if self.nic == _[1]:
                nic, addrs, nstat, iostat = _
                self.speed, self.duplex, self.mtu, self.isup, self.bytes_recv, self.bytes_sent, self.packets_recv, \
                    self.packets_sent, self.errin, self.errout, self.dropin, self.dropout = [None] * 12
                if self.exists(nstat):
                    self.speed = nstat[int('1')]
                    self.duplex = self.set_duplex_type(nstat[int('2')])
                    self.mtu = nstat[int('3')]
                    self.isup = True if nstat[int('4')] else False
                if self.exists(iostat):
                    self.bytes_recv = bytes2human(iostat.bytes_recv)
                    self.bytes_sent = bytes2human(iostat.bytes_sent)
                    self.packets_recv = iostat.packets_recv
                    self.packets_sent = io_counters.packets_sent
                    self.errin = io_counters.errin
                    self.errout = io_counters.errout
                    self.dropin = io_counters.dropin
                    self.dropout = io_counters.dropout





def interfaces() -> list[Iface]:
    nstats, iostats, nstat, iostat = psutil.net_if_stats(), psutil.net_io_counters(pernic=True), None, None
    nics_addrs = psutil.net_if_addrs()
    ifaces = []
    for nic, addrs in nics_addrs.items():
        nstat = n if (n := nstats[nic]) else None
        iostat = io if (io := nstats[nic]) else None
        ifaces.append(Iface(nic, addrs, nstat, iostat))
    return ifaces

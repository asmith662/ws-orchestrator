import socket

import psutil

from src.models.fmt import Fmt


class IAddr:
    address_family_map = {
        socket.AF_INET: 'IPv4',
        socket.AF_INET6: 'IPv6',
        psutil.AF_LINK: 'MAC',
    }

    def __init__(self, addr):
        self.family, self.address, self.broadcast, self.netmask, self.p2p = None, None, None, None, None
        if addr:
            self.family = self.set_addrs_family(addr.family, addr.family)
            self.address = addr.address
            self.broadcast = addr.broadcast
            self.netmask = addr.netmask
            self.p2p = addr.ptp

    def __iter__(self):
        return self

    def __next__(self):
        return self

    def __repr__(self):
        return repr(f'IAddr("{self.family}","{self.address}","{self.broadcast}","{self.netmask}","{self.p2p}")')

    def __str__(self):
        addr = Fmt.t(f'{self.family} address   : {self.address}', 1)
        broadcast = Fmt.t(f'broadcast : {self.broadcast}', 3)
        netmask = Fmt.t(f'netmask : {self.netmask}', 3)
        p2p = Fmt.t(f'p2p : {self.p2p}', 3)
        return Fmt.m(addr, broadcast, netmask, p2p)

    @classmethod
    def set_addrs_family(cls, key, val):
        return cls.address_family_map.get(key, val)

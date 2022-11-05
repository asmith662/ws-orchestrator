from src.models.fmt import Fmt
from src.models.interface.iaddr import IAddr
from src.models.interface.iostat import IOStat
from src.models.interface.istat import IStat


class Iface:
    def __init__(self, iface, addrs, stats, io_counter):
        self.iface = iface
        self.istats = IStat(stats)
        self.iostats = IOStat(io_counter)
        self.addrs = [IAddr(addr) for addr in addrs]

    def __repr__(self):
        return repr(f'Iface("{self.iface}",[{self.istats}],[{self.iostats}],[{self.addrs}])')

    def __iter__(self):
        return self

    def __next__(self):
        if not (self.iface and self.addrs):
            raise StopIteration
        return self

    def __str__(self):
        return Fmt.m(self.iface, Fmt.t(self.istats, 1), Fmt.t(self.iostats, 1), Fmt.t(self.addrs, 1))



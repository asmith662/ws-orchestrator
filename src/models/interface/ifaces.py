import psutil
from psutil._common import snicstats, snetio

from src.models.interface.iface import Iface


def nics() -> dict:
    return psutil.net_if_addrs()


def nstats() -> dict[str, snicstats]:
    return psutil.net_if_stats()


def iostats() -> snetio:
    return psutil.net_io_counters(pernic=True)


def findn(nic, stat_type: dict[str, snicstats] or snetio) -> bool:
    return nic in stat_type


def ifaces() -> [Iface]:
    ncs, stats, io_counters, st, io = nics(), nstats(), iostats(), None, None
    i_lst = []
    for nic, addrs in ncs.items():
        if findn(nic, stats):
            st = stats[nic]
        if findn(nic, io_counters):
            io = io_counters[nic]
        iface = Iface(nic, addrs, st, io)
        i_lst.append(iface)
    return i_lst

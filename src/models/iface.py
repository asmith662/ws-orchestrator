import socket

import psutil
from psutil._common import snicstats, snetio, bytes2human

# -------------------------------------------------Interface Init Data--------------------------------------------------
# --------------------------------------------------------Begin---------------------------------------------------------

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


def get_nics() -> dict:
    return psutil.net_if_addrs()


def nic_stats() -> dict[str, snicstats]:
    return psutil.net_if_stats()


# io = input-output
def io_stats() -> snetio:
    return psutil.net_io_counters(pernic=True)


def nic_in(nic, stat_type: dict[str, snicstats] or snetio) -> bool:
    return nic in stat_type


def get_data(data, *args) -> tuple or None:
    return tuple(args) if data else None


# -------------------------------------------------Interface Init Data--------------------------------------------------
# ---------------------------------------------------------End----------------------------------------------------------


# ---------------------------------------------------Interface Class----------------------------------------------------
# --------------------------------------------------------Begin---------------------------------------------------------

def repr_helper(addr):
    lb, rb = '{', '}'
    af, ip, b, n, p2p = addr['address_family'], addr['ip_address'], addr['broadcast'], addr['netmask'], addr['p2p']
    return f'{lb}"{af}","{ip}","{b}","{n}","{p2p}"{rb}'


class IStat:
    def __init__(self, stats):
        args = stats.speed, duplex_type_map[stats.duplex], stats.mtu, True if stats.isup else False
        self.speed, self.duplex, self.mtu, self.is_up = get_data(stats, *args)

    def __repr__(self):
        return repr(f'IStat({self.speed},"{self.duplex}"]",{self.mtu},{self.is_up})')

    def __str__(self):
        return f"""
    stats          : speed={self.speed}MB, duplex={self.duplex}, mtu={self.mtu}, up={self.is_up}"""

    def __iter__(self):
        return self

    def __next__(self):
        return self


class IOStat:
    def __init__(self, io_counters):
        args = bytes2human(io_counters.bytes_recv), bytes2human(io_counters.bytes_sent), io_counters.packets_recv, \
               io_counters.packets_sent, io_counters.errin, io_counters.errout, io_counters.dropin, io_counters.dropout
        self.b_received, self.b_sent, self.p_received, self.p_sent, self.s_errs, self.r_errs, self.i_drops, \
            self.o_drops = get_data(io_counters, *args)

    def __repr__(self):
        return repr(f'IOStat({self.b_received},{self.b_sent},{self.p_received},{self.p_sent},{self.s_errs},'
                    f'{self.r_errs},{self.i_drops},{self.o_drops})')

    def __str__(self):
        return \
            f"""
    incoming       : bytes={self.b_received}, pkts={self.p_received}, errs={self.r_errs}, drops={self.i_drops}
    outgoing       : bytes={self.b_sent}, pkts={self.p_sent}, errs={self.s_errs}, drops={self.o_drops}
            """

    def __iter__(self):
        return self

    def __next__(self):
        return self


class IAddr:
    def __init__(self, addr):
        args = address_family_map.get(addr.family, addr.family), addr.address, addr.broadcast, addr.netmask, addr.ptp
        self.addrs_family, self.ip_addrs, self.broadcast, self.netmask, self.p2p = get_data(addr, *args)

    def __repr__(self):
        return repr(f'IAddr("{self.addrs_family}","{self.ip_addrs}","{self.broadcast}","{self.netmask}","{self.p2p}")')

    def __str__(self):
        return \
            f"""
    {self.addrs_family} address   : {self.ip_addrs}
            broadcast : {self.broadcast}
            netmask   : {self.netmask}
            p2p       : {self.p2p}
            """

    def __iter__(self):
        return self

    def __next__(self):
        return self


class Iface:
    # the __init__() is the method used to create the Iface object
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
        return \
            f"""
{self.iface}
    {self.istats}
    {self.iostats}
    {self.addrs}
            """


# creates a list of Iface objects
def ifaces():
    nics, stats, io_counters, st, io = get_nics(), nic_stats(), io_stats(), None, None
    i_lst = []
    for nic, addrs in nics.items():
        if nic_in(nic, stats):
            st = stats[nic]
        if nic_in(nic, io_counters):
            io = io_counters[nic]
        iface = Iface(nic, addrs, st, io)
        i_lst.append(iface)
    return i_lst

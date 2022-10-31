import socket

import psutil
from psutil._common import snicstats, snetio, bytes2human

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


class Interface:
    def __init__(self, nic, addrs, stats, io_counter):
        self.nic = nic
        self.addrs = addrs
        self.stats = stats
        self.io_counter = io_counter
        if stats:
            print(stats)
            self.speed = stats.speed
            self.duplex = duplex_type_map[stats.duplex]
            self.mtu = stats.mtu
            self.is_up = True if stats.isup else False
        if io_counter:
            # b = bytes
            self.b_received = bytes2human(io_counter.bytes_recv)
            self.b_sent = bytes2human(io_counter.bytes_sent)
            # p = packets
            self.p_received = io_counter.packets_recv
            self.p_sent = io_counter.packets_sent
            self.err_receiving = io_counter.errin
            self.err_sending = io_counter.errout
            self.drops_in = io_counter.dropin
            self.drops_out = io_counter.dropout
        for addr in self.addrs:
            self.address_family = address_family_map.get(addr.family, addr.family)
            self.address = addr.address
            self.broadcast = addr.broadcast
            self.netmask = addr.netmask
            self.p2p = addr.ptp

    def print_stats(self):
        up, er, es = True if self.is_up else False, self.err_receiving, self.err_sending
        print(
            f"""
                stats          : speed={self.speed}MB, duplex={self.duplex}, mtu={self.mtu}, up={up}
                incoming       : bytes={self.b_received}, pkts={self.p_received}, errs={er}, drops={self.drops_in}
                outgoing       : bytes={self.b_sent}, pkts={self.p_sent}, errs={es}, drops={self.drops_out}
                {self.address_family} address   : {self.address}
                    broadcast : {self.broadcast}
                    netmask   : {self.netmask}
                    p2p       : {self.p2p}
            """)


def get_interfaces():
    nics, stats, io_counters, st, io = get_nics(), nic_stats(), io_stats(), None, None
    ifaces = []
    for nic, addrs in nics:
        print(nic, addrs)
        if nic_in(nic, stats):
            st = stats[nic]
        if nic_in(nic, io_counters):
            io = io_counters[nic]
    #         ifaces.append(Interface(nic, addrs, st, io))
    # return ifaces

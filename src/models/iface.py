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


class IfaceStat:
    def __init__(self, stats):
        args = stats.speed, duplex_type_map[stats.duplex], stats.mtu, True if stats.isup else False
        self.speed, self.duplex, self.mtu, self.is_up = get_data(stats, *args)

    def __iter__(self):
        return self

    def __next__(self):
        return self


class IoStat:
    def __init__(self, io_counters):
        args = bytes2human(io_counters.bytes_recv), bytes2human(io_counters.bytes_sent), io_counters.packets_recv, \
               io_counters.packets_sent, io_counters.errin, io_counters.errout, io_counters.dropin, io_counters.dropout
        self.b_received, self.b_sent, self.p_received, self.p_sent, self.s_errs, self.r_errs, self.i_drops, \
            self.o_drops = get_data(io_counters, *args)

    def __iter__(self):
        return self

    def __next__(self):
        return self


class IfaceAddr:
    def __init__(self, addr):
        args = address_family_map.get(addr.family, addr.family), addr.address, addr.broadcast, addr.netmask, addr.ptp
        self.addrs_family, self.ip_addrs, self.broadcast, self.netmask, self.p2p = get_data(addr, *args)

    def __iter__(self):
        return self

    def __next__(self):
        return self


class Iface:
    # the __init__() is the method used to create the Iface object
    def __init__(self, iface, addrs, stats, io_counter):
        self.iface = iface
        self.istats = IfaceStat(stats)
        self.iostats = IoStat(io_counter)
        self.addrs = [IfaceAddr(addr) for addr in addrs]

    # extremely critical note:
    # if you store a bunch of these Iface objects in a list
    # you can't use a for loop to iterate the list of objects out-of-the-box when you create a new class
    # you must include both __iter__() and __next__() methods
    # even still to iterate through a list of these objects you must use the syntax as shown in example:
    #
    # (this code should be placed where you want to create the object such as an attribute in the Network Class)
    # i = iter(ifaces())  <= here notice the iter() method this is a for loop
    # print((next(i)))    <= next is the the current object in the for loop runs, which is being printed

    def __iter__(self):
        return self

    def __next__(self):
        if not (self.iface and self.addrs):
            raise StopIteration
        return self

    # this method overrides the objects print method and can be called as shown in example:
    # either by directly using print(Iface) on the Iface object or
    # when used with the iter() method it can be used with print(next(Iface))
    # def __str__(self):
    #     up, er, es = True if self.is_up else False, self.receiving_errs, self.sending_errs
    #     return \
    #         f"""
    #             stats          : speed={self.speed}MB, duplex={self.duplex}, mtu={self.mtu}, up={up}
    #             incoming       : bytes={self.b_received}, pkts={self.p_received}, errs={er}, drops={self.in_drops}
    #             outgoing       : bytes={self.b_sent}, pkts={self.p_sent}, errs={es}, drops={self.out_drops}
    #             {self.addrs_family} address   : {self.ip_addrs}
    #                 broadcast : {self.broadcast}
    #                 netmask   : {self.netmask}
    #                 p2p       : {self.p2p}
    #         """

    # def __repr__(self): lb, rb, lsb, rsb = '(', ')', '[', ']' speed, duplex, mtu, is_up, b_received, b_sent,
    # p_received, p_sent, s_errs, r_errs, in_drops, out_drops = get_data( self) addrs = ','.join([repr_helper(a) for
    # a in addr_dict_lst(self)])
    #
    #     return repr(f'Iface("{self.iface}",' +
    #                 f'{lb}"{speed}","{duplex}","{mtu}","{is_up}"{rb},' +
    #                 f'{lb}"{b_received}","{p_received}","{r_errs}","{in_drops}"{rb},' +
    #                 f'{lb}"{b_sent}","{p_sent}","{s_errs}","{out_drops}"{rb},' +
    #                 f'{lsb}{addrs}{rsb})'
    #                 )

    # def to_dict(self): speed, duplex, mtu, is_up, b_received, b_sent, p_received, p_sent, s_errs, r_errs, in_drops,
    # out_drops = get_data( self) return { 'iface': self.iface, 'stats': { 'speed': speed, 'duplex': duplex,
    # 'mtu': mtu, 'is_up': is_up }, 'incoming': { 'bytes_received': b_received, 'packets_received': p_received,
    # 'receiving_errors': r_errs, 'incoming_drops': in_drops }, 'outgoing': { 'bytes_sent': b_sent, 'packets_sent':
    # p_sent, 'sending_errors': s_errs, 'outgoing_drops': out_drops }, 'addrs': addr_lst() }

    # def get_data(self):
    #     if self.stats:
    #         speed, duplex, mtu, is_up = self.speed, self.duplex, self.mtu, self.is_up
    #     else:
    #         speed, duplex, mtu, is_up = (None for i in range(3))
    #     if self.io_counter:
    #         b_received, b_sent, p_received, p_sent = self.b_received, self.b_sent, self.p_received, self.p_sent
    #         s_errs, r_errs, i_drops, o_drops = self.sending_errs, self.receiving_errs, self.in_drops, self.out_drops
    #
    #     else:
    #         b_received, b_sent, p_received, p_sent, s_errs, r_errs, i_drops, o_drops = (None for i in range(7))
    #     return speed, duplex, mtu, is_up, b_received, b_sent, p_received, p_sent, s_errs, r_errs, i_drops, o_drops
    #
    # def addr_dict_lst(self):
    #     return [
    #         {
    #             'address_family': self.addrs_family,
    #             'ip_address': self.ip_addrs,
    #             'broadcast': self.broadcast,
    #             'netmask': self.netmask,
    #             'p2p': self.p2p
    #         }
    #         for a in self.addrs
    #     ]
    #
    # def set_addrs(self):
    #     for addr in self.addrs:
    #         self.addrs_family = address_family_map.get(addr.family, addr.family)
    #         self.ip_addrs = addr.ip_addrs
    #         self.broadcast = addr.broadcast
    #         self.netmask = addr.netmask
    #         self.p2p = addr.ptp


# ---------------------------------------------------Interface Class----------------------------------------------------
# ---------------------------------------------------------End----------------------------------------------------------

# creates a list of Iface objects for the interfaces that are discovered on the network
# retrieves statistics about all nics and i/o data, which is filtered into each Iface object during creation
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

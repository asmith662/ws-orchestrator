import psutil
import socket

from psutil._common import bytes2human

from src.models.resources.mixins import Fmt


class Interfaces:

    def __init__(self):
        self.interfaces = self._get()

    def __iter__(self):
        return self

    def __next__(self):
        for count, interface in enumerate(self.interfaces):
            if count == len(self.interfaces):
                raise StopIteration
            else:
                return interface

    @classmethod
    def _get(cls):
        nstats = psutil.net_if_stats()
        iostats = psutil.net_io_counters(pernic=True)
        nics_addrs = psutil.net_if_addrs()
        return [Interface(nic, addrs, nstats, iostats) for nic, addrs in nics_addrs.items()]


class Interface:
    duplex_type_map = {
        psutil.NIC_DUPLEX_FULL: "full",
        psutil.NIC_DUPLEX_HALF: "half",
        psutil.NIC_DUPLEX_UNKNOWN: "?",
    }

    def __init__(self, nic, addrs, nstats, iostats):
        self.nic = nic
        self.addrs = addrs
        self.nstats = nstats
        self.iostats = iostats
        self._set()

    def __repr__(self):
        return repr(f'Iface("{self.nic}",{self.speed},"{self.duplex}"]",{self.mtu},{self.isup},{self.incoming},'
                    f'{self.outgoing},[{self.addrs}]')

    def __iter__(self):
        return self

    def __next__(self):
        if not (self.nic and self.addrs):
            raise StopIteration
        return self

    def __str__(self):
        i, o = self.incoming, self.outgoing
        r1 = f'[{self.nic}]'
        r2 = Fmt.t(f'stats       : speed={self.speed}MB, duplex={self.duplex}, mtu={self.mtu}, up={self.isup}')
        r3 = Fmt.t(f'incoming    : bytes={i.bytes_recv}, pkts={i.packets_recv}, errs={i.errin}, drops={i.dropin}')
        r4 = Fmt.t(f'outgoing    : bytes={o.bytes_sent}, pkts={o.packets_sent}, errs={o.errout}, drops={o.dropout}')
        rows = [r1, r2, r3, r4] + [Fmt.t(str(a), 2) for a in self.addrs]
        return Fmt.m(*rows)

    @classmethod
    def _duplex(cls, duplex):
        return cls.duplex_type_map[duplex]

    def _set(self):
        if self.nic in self.nstats:
            st = self.nstats[self.nic]
            self.speed = st.speed
            self.duplex = self._duplex(st.duplex)
            self.mtu = st.mtu
            self.isup = True if st.isup else False
        if self.nic in self.iostats:
            io = self.iostats[self.nic]
            self.incoming = Incoming(bytes2human(io.bytes_recv), io.packets_recv, io.errin, io.dropin)
            self.outgoing = Outgoing(bytes2human(io.bytes_sent), io.packets_sent, io.errout, io.dropout)
        self.addrs = [Address(addr) for addr in self.addrs]


class Incoming:
    def __init__(self, bytes_recv, packets_recv, errin, dropin):
        self.bytes_recv = bytes_recv
        self.packets_recv = packets_recv
        self.errin = errin
        self.dropin = dropin

    def __repr__(self):
        return repr(f'Incoming({self.bytes_recv},{self.packets_recv},{self.errin},{self.dropin})')


class Outgoing:
    def __init__(self, bytes_sent, packets_sent, errout, dropout):
        self.bytes_sent = bytes_sent
        self.packets_sent = packets_sent
        self.errout = errout
        self.dropout = dropout

    def __repr__(self):
        return repr(f'Outgoing({self.bytes_sent},{self.packets_sent},{self.errout},{self.dropout})')


class Address:
    address_family_map = {
        socket.AF_INET: 'IPv4',
        socket.AF_INET6: 'IPv6',
        psutil.AF_LINK: 'MAC ',
    }

    def __init__(self, addr):
        self.family = self._family(addr.family, addr.family)
        self.address = addr.address
        self.broadcast = addr.broadcast
        self.netmask = addr.netmask
        self.p2p = addr.ptp

    def __repr__(self):
        return repr(f'Address("{self.family}","{self.address}","{self.broadcast}","{self.netmask}","{self.p2p}"')

    def __str__(self):
        return \
            f'{self.family}    : address={self.address}, broadcast={self.broadcast}, netmask={self.netmask}, ' \
            f'p2p={self.p2p}'

    @classmethod
    def _family(cls, key, val):
        return cls.address_family_map.get(key, val)

import psutil

from src.models.fmt import Fmt


class IStat:
    duplex_type_map = {
        psutil.NIC_DUPLEX_FULL: "full",
        psutil.NIC_DUPLEX_HALF: "half",
        psutil.NIC_DUPLEX_UNKNOWN: "?",
    }

    def __init__(self, stats):
        self.speed, self.duplex, self.mtu, self.isup = None, None, None, None
        if stats:
            self.speed = stats.speed
            self.duplex = self.set_duplex_type(stats.duplex)
            self.mtu = stats.mtu
            self.isup = True if stats.isup else False

    def __iter__(self):
        return self

    def __next__(self):
        return self

    def __repr__(self):
        return repr(f'IStat({self.speed},"{self.duplex}"]",{self.mtu},{self.isup})')

    def __str__(self):
        return Fmt.t(f'stats          : speed={self.speed}MB, duplex={self.duplex}, mtu={self.mtu}, up={self.isup}',
                     1)

    @classmethod
    def set_duplex_type(cls, duplex):
        return cls.duplex_type_map[duplex]

from psutil._common import bytes2human

from src.models.fmt import Fmt


class IOStat:
    def __init__(self, io_counters):
        self.bytes_recv, self.bytes_sent, self.packets_recv, self.packets_sent, self.errin, self.errout, self.dropin, \
            self.dropout = None, None, None, None, None, None, None, None
        if io_counters:
            self.bytes_recv = bytes2human(io_counters.bytes_recv)
            self.bytes_sent = bytes2human(io_counters.bytes_sent)
            self.packets_recv = io_counters.packets_recv
            self.packets_sent = io_counters.packets_sent
            self.errin = io_counters.errin
            self.errout = io_counters.errout
            self.dropin = io_counters.dropin
            self.dropout = io_counters.dropout

    def __iter__(self):
        return self

    def __next__(self):
        return self

    def __repr__(self):
        return repr(
            f'IOStat({self.bytes_recv},{self.bytes_sent},{self.packets_recv},{self.packets_sent},{self.errin},'
            f'{self.errout},{self.dropin},{self.dropout})')

    def __str__(self):
        spacer = '       : bytes='
        i = f'incoming{spacer}: bytes={self.bytes_recv}, pkts={self.packets_recv}, errs={self.errout}, drops={self.dropin}'
        o = f'outgoing{spacer}: bytes={self.bytes_sent}, pkts={self.packets_sent}, errs={self.errin}, drops={self.dropout}'
        return Fmt.m(Fmt.tab(i, 1), Fmt.t(o, 1))

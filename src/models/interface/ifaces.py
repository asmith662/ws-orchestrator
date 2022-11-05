from typing import Dict, List

import psutil
from psutil._common import snicaddr, snicstats, snetio


class Ifaces:
    def __init__(self):
        self.nics = self._nics()

    @staticmethod
    def _nics() -> dict[str, list[snicaddr]]:
        return psutil.net_if_addrs()

    @staticmethod
    def _nstats() -> dict[str, snicstats]:
        return psutil.net_if_stats()

    @staticmethod
    def _iostats() -> snetio:
        return psutil.net_io_counters(pernic=True)

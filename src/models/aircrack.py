"""
------------------------------------------------------------------------------------------------------------------------
Acronyms List:
------------------------------------------------------------------------------------------------------------------------
    wl = word list
    fp = file path
    fn = file name
    ext = extension
------------------------------------------------------------------------------------------------------------------------
"""
import os

from src.models.cmd import stream_cmd_hidden, stream_cmd


class Aircrack:
    def __init__(self, cap_fp, wl_fp):
        self.cap_fp = cap_fp
        self.wl_fp = wl_fp

        self.ready_check()

    def start_aircrack(self):
        wl_exts = ['json', 'txt', 'xml', 'csv']
        if self.cap_fp.split(".")[1] == "cap" and self.wl_fp.split(".")[1] in wl_exts:
            stream_cmd_hidden(f'sudo aircrack-ng -w {self.wl_fp} {self.cap_fp}')

    def start_hashcat(self):
        fn, ext = self.cap_fp.split(".")
        if ext == "cap":
            stream_cmd_hidden(f"sudo hashcat -m 22000 {fn}.22000 {self.wl_fp}")

    def ready_check(self):
        if os.path.isfile(self.cap_fp) and os.path.isfile(self.wl_fp):
            self.start_aircrack()
            self.start_hashcat()

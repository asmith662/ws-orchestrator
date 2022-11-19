import os

from .executor import Executor


class AircrackNg(Executor):
    """ Aircrack-ng 1.6  - (C) 2006-2020 Thomas d'Otreppe
  https://www.aircrack-ng.org
  Usage: aircrack-ng [options] <file>...
  Options:
      -a <amode> : force attack mode (1/WEP, 2/WPA-PSK)
      -e <essid> : target selection: network identifier
      -b <bssid> : target selection: access point's MAC
      -p <nbcpu> : # of CPU to use  (default: all CPUs)
      -q         : enable quiet mode (no status output)
      -C <macs>  : merge the given APs to a virtual one
      -l <file>  : write key to file. Overwrites file.
      -c         : search alpha-numeric characters only
      -t         : search binary coded decimal chr only
      -h         : search the numeric key for Fritz!BOX
      -d <mask>  : use masking of the key (A1:XX:CF:YY)
      -m <maddr> : MAC address to filter usable packets
      -n <nbits> : WEP key length :  64/128/152/256/512
      -i <index> : WEP key index (1 to 4), default: any
      -f <fudge> : bruteforce fudge factor,  default: 2
      -k <korek> : disable one attack method  (1 to 17)
      -x or -x0  : disable bruteforce for last keybytes
      -x1        : last keybyte bruteforcing  (default)
      -x2        : enable last  2 keybytes bruteforcing
      -X         : disable  bruteforce   multithreading
      -y         : experimental  single bruteforce mode
      -K         : use only old KoreK attacks (pre-PTW)
      -s         : show the key in ASCII while cracking
      -M <num>   : specify maximum number of IVs to use
      -D         : WEP decloak, skips broken keystreams
      -P <num>   : PTW debug:  1: disable Klein, 2: PTW
      -1         : run only 1 try to crack key with PTW
      -V         : run in visual inspection mode
      -w <words> : path to wordlist(s) filename(s)
      -N <file>  : path to new session filename
      -R <file>  : path to existing session filename
      -E <file>  : create EWSA Project file v3
      -I <str>   : PMKID string (hashcat -m 16800)
      -j <file>  : create Hashcat v3.6+ file (HCCAPX)
      -J <file>  : create Hashcat file (HCCAP)
      -S         : WPA cracking speed test
      -Z <sec>   : WPA cracking speed test length of
                   execution.
      -r <DB>    : path to airolib-ng database
      --simd-list       : Show a list of the available
      --simd <option>   : Use specific SIMD architecture.
      -u         : Displays # of CPUs & SIMD support
      --help     : Displays this usage screen
    """
    command = "aircrack-ng"
    requires_tempfile = True
    requires_tempdir = False
    requires_root = True

    async def run(self, *args, **kwargs):
        if self.tempfile:
            kwargs['l'] = self.tempfile.name
        return await super().run(*args, **kwargs)

    async def get_result(self):
        """Read tempfile (write key result)"""
        if self.proc:
            await self.proc.wait()
        if self.tempfile:
            return self.tempfile.read()

# class AircrackNg:
#     def __init__(self, cap_fp, wl_fp):
#         self.cap_fp = cap_fp
#         self.wl_fp = wl_fp
#
#         self.ready_check()
#
#     def start_aircrack(self):
#         wl_exts = ['json', 'txt', 'xml', 'csv']
#         if self.cap_fp.split(".")[1] == "cap" and self.wl_fp.split(".")[1] in wl_exts:
#             run_background_cmd(f'sudo aircrack-ng -w {self.wl_fp} {self.cap_fp}')
#
#     def start_hashcat(self):
#         fn, ext = self.cap_fp.split(".")
#         if ext == "cap":
#             run_background_cmd(f"sudo hashcat -m 22000 {fn}.22000 {self.wl_fp}")
#
#     def ready_check(self):
#         if os.path.isfile(self.cap_fp) and os.path.isfile(self.wl_fp):
#             self.start_aircrack()
#             self.start_hashcat()

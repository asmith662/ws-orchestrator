import re
import sys


class Test:
    """
    Name: aircrack-ng - a 802.11 WEP / WPA-PSK key cracker

    Synopsis: aircrack-ng [options] <.cap / .ivs file(s)>

    Description: aircrack-ng is a 802.11 WEP / WPA-PSK key cracker. It implements the so-called Fluhrer - Mantin -
    Shamir (FMS) attack, along with some new attacks by a talented hacker named KoreK. When enough encrypted packets
    have been gathered, aircrack-ng can almost instantly recover the WEP key.

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
        -Z <sec>   : WPA cracking speed test length of execution.
        -r <DB>    : path to airolib-ng database
        --simd-list       : Show a list of the available
        --simd <option>   : Use specific SIMD architecture.
        -u         : Displays # of CPUs & SIMD support
        --help     : Displays this usage screen
    """


class OptsParser:
    def __init__(self, docstring):
        if not docstring:
            self.docstring, self.name, self.args, self.kwargs = '', None, [], {}
        else:
            self.docstring = docstring
            self.name, self.args = self.usage(self._rows(docstring))

    @staticmethod
    def calc_indent(docstring):

    @classmethod
    def _rows(cls, docstring):
        if not docstring:
            return ['']
        lines = docstring.expandtabs().splitlines()
        max_indent = sys.maxsize
        for line in lines:
            if stripped := line.strip():
                max_indent = min(max_indent, len(line) - len(stripped))
        return [line[max_indent:].strip() for line in lines if line != ''] if max_indent < sys.maxsize else ['']

    @classmethod
    def _sections

    @classmethod
    def _inrow(cls, row, *args):
        for arg in args:
            if arg in row.lower():
                return True
        return False

    @staticmethod
    def usage(rows):
        for r in rows:
            if OptsParser.c('usage:'):
                section, name, args = r.replace('[options] ', '').split(' ', 2)
                args = [a[1:-1] for a in re.findall(r'<.+>|\[.+]', args)]
                return name, args

    @staticmethod
    def _options(rows):
        for r in rows:
            if OptsParser.c('options:'):

    @staticmethod
    def data(docstring):
        details = {}
        rows = OptsParser._rows(docstring)
        row_num = 0
        opt_types = []
        row_num = 0
        for r in rows[(row_num - 1):]:
            print(r)
            row_num += 1
            if 'options:' in r.lower():
                opt_types.append(r[:-9])
            print(r)
            if re.search(r'^(--|-)', r):
                print(r)
        print(opt_types)

    c = check

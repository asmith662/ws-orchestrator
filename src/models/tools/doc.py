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


class OptsDoc:

    @staticmethod
    def _rows(docstring):
        if not docstring:
            return ['']
        lines = docstring.expandtabs().splitlines()
        max_indent = sys.maxsize
        for line in lines:
            if stripped := line.strip():
                max_indent = min(max_indent, len(line) - len(stripped))
        return [line[max_indent:].strip() for line in lines if line != ''] if max_indent < sys.maxsize else ['']

    @staticmethod
    def usage(docstring):
        usage = [r.split() for r in OptsDoc._rows(docstring) if 'usage:' in r.lower()][0]
        print(usage[3][1:-1])
        return {'name': usage[1], 'section': usage[2], }

    @staticmethod
    def _search(heading, row):
        return row if f'{heading}:' in row.lower() else None

    @staticmethod
    def data(docstring):
        details = {}
        rows, row_num = OptsDoc._rows(docstring), 0
        desc_start, desc_end, opts_start, opts_end = [None] * 4
        for r in OptsDoc._rows(docstring):
            row_num += 1
            if 'name:' in r.lower():
                details.update(fullname=(r.split(':')[1].strip()), name=r.split()[1])
            elif 'synopsis:' in r.lower():
                details.update(files=True if r.split(']')[1].strip()[1:-1] != '' else False)
            elif 'description:' in r.lower():
                desc_start = row_num - 1
            elif 'options:' in r.lower():
                desc_end, opts_start, opts_end = row_num - 1, row_num, len(rows)
        details.update(description=' '.join(rows[desc_start:desc_end])[13:])
        options = rows[opts_start:opts_end]
        print(details)
        print(options)
    s = _search

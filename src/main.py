import asyncio
import getpass
import logging
import os.path
import re
import subprocess
import pexpect
from logging.handlers import RotatingFileHandler

# logger
log_path = os.path.realpath(os.path.join(os.path.dirname(__file__), 'ws-orchestrator.log'))
logging.basicConfig(
    handlers=[
        RotatingFileHandler(
            log_path,
            maxBytes=25000000,
            backupCount=5
        )
    ],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)

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

# Global variables
Interfaces = []
Interface = ""
Password = ''

# Arguments
DO_NOT_KILL = False
DONT_ASK_TO_SAVE_PASSWORD = False


def can_sudo(pwd: str = Password) -> bool:
    args = f" echo {pwd} | sudo -S -k iwconfig".split()
    kwargs = dict(stdout=subprocess.PIPE, encoding="ascii")
    if pwd:
        kwargs.update(input=pwd)
    print(args)
    cmd = subprocess.run(args, **kwargs)
    print(cmd.stdout)
    return "OK" in str(cmd.stdout)


def format_cmd(cmd: str, pwd: str = None) -> tuple:
    args = cmd.split()
    kwargs = dict(stdout=subprocess.PIPE, encoding="ascii")
    if pwd and can_sudo():
        kwargs.update(input=pwd)
    return args, kwargs,


def get_cmd(cmd: str, pwd: str = None) -> tuple:
    if 'sudo' in cmd:
        root = os.geteuid() == 0
        if not (root and pwd):
            pwd = get_pass()
            return format_cmd(cmd, pwd)
        else:
            if DONT_ASK_TO_SAVE_PASSWORD:
                return format_cmd(cmd, pwd)
            elif can_sudo(pwd):
                return format_cmd(cmd, pwd)
    else:
        return format_cmd(cmd)


def run_cmd(cmd: str, pwd: str = None):
    out = os.system(f"echo {pwd} | sudo -S {cmd}")
    print(out)
    # args, kwargs = get_cmd(cmd, pwd)
    # cmd = subprocess.run(args, **kwargs)
    # print(cmd)


def stream_cmd(cmd: str, pwd: str = Password) -> str:
    # if 'sudo' in cmd and pwd != '':
    # args = cmd
    pswd = get_pass()
    # return os.popen(cmd).read()
    p = subprocess.Popen(['sudo', '-S', cmd], stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    err = None
    try:
        out, err = p.communicate(input=(pswd + '\n').encode(), timeout=5)
        return out.decode()
    except subprocess.TimeoutExpired:
        logging.warning("Killing processes due to:", err.decode())
        p.kill()


def stream_cmd_hidden(cmd: str):
    pswd = get_pass()
    p = subprocess.Popen(['sudo', '-S', cmd], stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    try:
        out, err = p.communicate(input=(pswd + '\n').encode(), timeout=5)
        return out, err,
    except subprocess.TimeoutExpired:
        p.kill()


def get_pass():
    pwd = getpass.getpass(prompt='[sudo] password for {user}: ')
    if can_sudo(pwd):
        if not DONT_ASK_TO_SAVE_PASSWORD:
            save_prompt(pwd)
        return pwd
    else:
        get_pass()


def save_prompt(pswd):
    global Password, DONT_ASK_TO_SAVE_PASSWORD
    save = input('Save password for future commands that require sudo? \'y\' | \'n\'\n')
    if save == 'y' or save == 'n':
        if save == 'y':
            Password = pswd
        elif save == 'n':
            ask = input('Don\'t ask to save password again? \'y\' | any key to cancel\n')
            if ask == 'y':
                DONT_ASK_TO_SAVE_PASSWORD = True
    else:
        save_prompt(pswd)


def check_monitor_mode(interface):
    command_get_mode = f"sudo iwconfig {interface} | awk -F: '/Mode/{{print$2}}'"
    if stream_cmd(command_get_mode).split(" ", 1)[0] == "Monitor":
        return True
    else:
        return False


def set_monitor_mode(interface, enable):
    if enable:
        if not DO_NOT_KILL:
            logging.info("Killing processes.")
            stream_cmd("sudo airmon-ng check kill")
        else:
            logging.info("NOT killing processes.", 1)
        logging.info(f"Starting airmon-ng on: {interface}.")
        stream_cmd(f"sudo airmon-ng start {interface}")
    else:
        logging.info(f"Stopping airmon-ng on: {interface}.")
        stream_cmd(f"sudo airmon-ng stop {interface}")
        logging.info("Starting Network Manager.")
        start_network_manager()


def start_network_manager():
    if "Unit dhcpcd.service" in stream_cmd("sudo systemctl start dhcpcd 2>&1"):
        stream_cmd("sudo systemctl start NetworkManager")


def restart_network_manager():
    if "Unit dhcpcd.service" in stream_cmd("sudo systemctl restart dhcpcd 2>&1"):
        stream_cmd("sudo systemctl restart NetworkManager")


def scan_networks():
    networks = []

    splitted_output_scan_wifi = stream_cmd("nmcli dev wifi").split("\n")
    del splitted_output_scan_wifi[0]

    if not splitted_output_scan_wifi:
        logging.info("No networks found", 2)
        return networks

    if splitted_output_scan_wifi[0] == '':
        logging.info("No networks found", 2)
        return networks

    for record in splitted_output_scan_wifi:
        record = re.sub(" +", " ", record).strip()

        splitted_record = record.split(" ")
        if splitted_record == ['']:
            continue

        if splitted_record[0] == '*':
            del splitted_record[0]

        # fix for names with spaces (note for my future self)
        i = 2
        while i < splitted_record.index("Infra"):
            splitted_record[1] += " " + splitted_record[i]
            splitted_record.remove(splitted_record[i])

        index_infra = splitted_record.index("Infra")
        del splitted_record[index_infra]
        del splitted_record[index_infra + 1]
        del splitted_record[index_infra + 1]
        del splitted_record[index_infra + 2]

        for index in range(index_infra + 2, len(splitted_record) - 1):
            splitted_record[index] += ", " + splitted_record[index + 1]
            splitted_record.remove(splitted_record[index + 1])

        networks.append(splitted_record)
    return networks


def update_interfaces():
    if Interfaces:
        del Interfaces[:]

    interfaces = stream_cmd('sudo iwconfig 2>&1 | grep -oP "^\\w+"').split("\n")[:-1]
    for interface in interfaces:
        print(interface)
        if interface != "lo" and interface != "eth0":
            stream_cmd(f"sudo ifconfig {interface} up")
            Interfaces.append(interface)

    if len(Interfaces) == 0:
        logging.info("Scanning for interfaces.")
        restart_network_manager()
        update_interfaces()
    else:
        print(i for i in Interfaces)


class Airodump:
    Network = []
    Station = ""
    Stations = []
    Directory = ""
    DeauthPackets = 10

    def __init__(self, network):
        # if not check_monitor_mode(Interface):
        #     pass

        logging.info(f"Starting airodump-ng on bssid: {self.Network[0]}")


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


async def main():
    if __name__ == '__main__':
        # result = await run_shell_cmd('echo "Hello, world!"')
        # print(result)
        pwd = input(' sudo password: ')  # hard-coded password for testing
        run_cmd('iwconfig', pwd)
        # update_interfaces()
        pass


asyncio.run(main())

# Global variables
import logging
import re
import socket

import psutil
from psutil._common import bytes2human

from src.models.cmd.cmd import run_cmd

Interfaces = []
Interface = ""

# Global Arguments
DO_NOT_KILL = False


def check_monitor_mode(interface):
    command_get_mode = f"iwconfig {interface} | awk -F: '/Mode/{{print$2}}'"
    if run_cmd(command_get_mode).split(" ", 1)[0] == "Monitor":
        return True
    else:
        return False


def set_monitor_mode(interface, enable):
    if enable:
        if not DO_NOT_KILL:
            logging.info("Killing processes.")
            run_cmd("airmon-ng check kill")
        else:
            logging.info("NOT killing processes.", 1)
        logging.info(f"Starting airmon-ng on: {interface}.")
        run_cmd(f"airmon-ng start {interface}")
    else:
        logging.info(f"Stopping airmon-ng on: {interface}.")
        run_cmd(f"airmon-ng stop {interface}")
        logging.info("Starting Network Manager.")
        start_network_manager()


def start_network_manager():
    if "Unit dhcpcd.service" in run_cmd("systemctl start dhcpcd 2>&1"):
        run_cmd("systemctl start NetworkManager")


def restart_network_manager():
    if "Unit dhcpcd.service" in run_cmd("systemctl restart dhcpcd 2>&1"):
        run_cmd("systemctl restart NetworkManager")


def scan_networks():
    networks = []

    splitted_output_scan_wifi = run_cmd("nmcli dev wifi").split("\n")
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


af_map = {
    socket.AF_INET: 'IPv4',
    socket.AF_INET6: 'IPv6',
    psutil.AF_LINK: 'MAC',
}

duplex_map = {
    psutil.NIC_DUPLEX_FULL: "full",
    psutil.NIC_DUPLEX_HALF: "half",
    psutil.NIC_DUPLEX_UNKNOWN: "?",
}


def update_interfaces():
    if Interfaces:
        del Interfaces[:]

    interfaces = run_cmd('iwconfig 2>&1 | grep -oP "^\\w+"').split("\n")[:-1]
    for interface in interfaces:
        print(interface)
        if interface != "lo" and interface != "eth0":
            run_cmd(f"ifconfig {interface} up")
            Interfaces.append(interface)

    if len(Interfaces) == 0:
        logging.info("Scanning for interfaces.")
        restart_network_manager()
        update_interfaces()
    else:
        print(i for i in Interfaces)


def get_interfaces():
    if Interfaces:
        del Interfaces[:]
    # interfaces = run_cmd('iwconfig 2>&1 | grep -oP "^\\w+"')
    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    io_counters = psutil.net_io_counters(pernic=True)
    for nic, addrs in psutil.net_if_addrs().items():
        print(f"{nic}:")
        if nic in stats:
            st = stats[nic]
            print("    stats          : ", end='')
            print("speed=%sMB, duplex=%s, mtu=%s, up=%s" % (
                st.speed, duplex_map[st.duplex], st.mtu,
                "yes" if st.isup else "no"))
        if nic in io_counters:
            io = io_counters[nic]
            print("    incoming       : ", end='')
            print("bytes=%s, pkts=%s, errs=%s, drops=%s" % (
                bytes2human(io.bytes_recv), io.packets_recv, io.errin,
                io.dropin))
            print("    outgoing       : ", end='')
            print("bytes=%s, pkts=%s, errs=%s, drops=%s" % (
                bytes2human(io.bytes_sent), io.packets_sent, io.errout,
                io.dropout))
        for addr in addrs:
            print("    %-4s" % af_map.get(addr.family, addr.family), end="")
            print(" address   : %s" % addr.address)
            if addr.broadcast:
                print("         broadcast : %s" % addr.broadcast)
            if addr.netmask:
                print("         netmask   : %s" % addr.netmask)
            if addr.ptp:
                print("      p2p       : %s" % addr.ptp)
        print("")
    # return run_cmd('iwconfig 2>&1 | grep -oP "^\\w+"')
# .split("\n")[:-1]

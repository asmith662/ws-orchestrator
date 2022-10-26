import logging

from src.main import DO_NOT_KILL
from src.models.cmd import stream_cmd


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

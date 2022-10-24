import logging


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

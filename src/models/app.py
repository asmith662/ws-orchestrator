import logging

from src.models.general.auth import Auth
from src.models.general.config import logger
from src.models.general.users import Users
from src.models.network.interfaces import Interfaces


class App:
    def __init__(self):
        # start logger
        self.logging_enabled = bool(logger())

        # get users
        self.users = Users()

        # authenticate to start app
        with Auth():
            self.interfaces = Interfaces().interfaces
            for i in self.interfaces:
                if 'wlan0' in i.nic:
                    is_up = i.isup
                    if not is_up:
                        logging.info('')

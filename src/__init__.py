import logging
import os
import re
import sys
from logging.handlers import RotatingFileHandler
import subprocess as sub
from subprocess import Popen, PIPE, DEVNULL

from .models.auth import Users, Auth, User


class Startup:
    def __init__(self):
        self.logging_enabled = bool(self.logger())
        self.banner(), self.cleanup()

    @staticmethod
    def logger():
        try:
            log_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../ws-orchestrator.log'))
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
            logging.info('Starting ws-orchestrator...')
            return True
        except Exception as e:
            print('While configuring logger, error:', e)
            return False

    @staticmethod
    def banner():
        return """
░██╗░░░░░░░██╗░██████╗░░░░░░░█████╗░██████╗░░█████╗░██╗░░██╗███████╗░██████╗████████╗██████╗░░█████╗░████████╗░█████╗░██████╗░
░██║░░██╗░░██║██╔════╝░░░░░░██╔══██╗██╔══██╗██╔══██╗██║░░██║██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗
░╚██╗████╗██╔╝╚█████╗░█████╗██║░░██║██████╔╝██║░░╚═╝███████║█████╗░░╚█████╗░░░░██║░░░██████╔╝███████║░░░██║░░░██║░░██║██████╔╝
░░████╔═████║░░╚═══██╗╚════╝██║░░██║██╔══██╗██║░░██╗██╔══██║██╔══╝░░░╚═══██╗░░░██║░░░██╔══██╗██╔══██║░░░██║░░░██║░░██║██╔══██╗
░░╚██╔╝░╚██╔╝░██████╔╝░░░░░░╚█████╔╝██║░░██║╚█████╔╝██║░░██║███████╗██████╔╝░░░██║░░░██║░░██║██║░░██║░░░██║░░░╚█████╔╝██║░░██║
░░░╚═╝░░░╚═╝░░╚═════╝░░░░░░░░╚════╝░╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝╚══════╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝       
        """

    @staticmethod
    def cleanup():
        user = os.getlogin()
        with Popen(f'ls /tmp'.split(), stderr=DEVNULL, stdout=PIPE) as proc_launch:
            files = proc_launch.communicate()[0].decode().split('\n')
        if fps := ' '.join(
                [f for f in ['/tmp/' + f for f in files] if re.search(f'^/tmp/' + user + '[a-z0-9_]+_key$', f)]):
            return True and logging.info(f'Removed "{files}" leftover from previous execution') \
                if sub.run(f'rm {fps}'.split()).returncode == 0 \
                else False and logging.warning('Failed to remove existing password files.')


def find_user() -> User:
    """Checks the username of the current user against all active users
    to retrieve a User object, which has additional details about the user.
    """
    username = u if (u := os.getlogin()) else logging.warning(Exception('ANONYMOUS_USER'))
    return user if (user := Users().get_user(username)) \
        else None and logging.warning(Exception('USER_NOT_FOUND')) and sys.exit()

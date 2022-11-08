import getpass
import logging
import os
import subprocess
import sys

from src.models.general.users import User, Users


class Auth:
    try_map = ['First', 'Second', 'Third', 'Fourth', 'Fifth']
    users = Users().users
    exist_msg = 'Sending shutdown signal..'

    def __init__(self, pwd=None, strict=False):
        self.isroot = os.geteuid() == 0
        self.username = self._user()
        if not self.isroot and self.username:
            if pwd:
                if self._can_sudo(pwd):
                    self.password = pwd
                else:
                    self.password = self._pwd_prompt(self.username, strict)

    def __repr__(self):
        return repr(f'Auth(isroot={self.isroot},username="{self.username}",password="{self.password}")')

    def __enter__(self):
        logging.info(f'{self.username} is now authenticated.')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.password = None
        logging.info(f'{self.username} is now signed-out.')

    @classmethod
    def _user(cls) -> User or None:
        e = Exception('USER_NOT_FOUND')
        return username if (username := os.getlogin()) else print(e), logging.warning(e), sys.exit(cls.exist_msg)

    @classmethod
    def _can_sudo(cls, pwd):
        kwargs = dict(stdout=subprocess.PIPE, encoding="ascii")
        if pwd:
            kwargs.update(input=pwd)
        return True if "confirmed" in str(subprocess.run(f"sudo -S echo confirmed".split(), **kwargs).stdout) else False

    @classmethod
    def _pwd_prompt(cls, username, strict) -> str:
        attempts = 5 if not strict else 3
        while not attempts == 0:
            pwd = input(f'Enter password for {username}:    ')
            if cls._can_sudo(pwd):
                return pwd
            else:
                attempts -= 1
                logging.warning(f'{cls.try_map[attempts]} failed password attempt for {username}')
        logging.warning(f'Too many failed password attempts for {username}.  {cls.exist_msg}'), sys.exit()

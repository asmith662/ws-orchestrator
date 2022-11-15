import logging
import os
import sys
import tempfile
import time
from contextlib import contextmanager
from subprocess import DEVNULL, check_output, check_call

import psutil
from rich.prompt import Prompt

from src.models.resources.mixins import Fmt

exist_msg = 'Sending shutdown signal..'


class User:
    username = u if (u := os.getlogin()) else logging.error(Exception('ANONYMOUS_USER')) and sys.exit()

    def __init__(self, password: str = None):
        user = self._user()
        self.isroot = os.geteuid() == 0
        self.username = user.name
        self.terminal = user.terminal
        self.host = user.host
        self.session = time.strftime("%H:%M:%S", time.gmtime(user.started))
        self.pid = user.pid
        if not self.isroot:
            self.secret_fp = self.authenticate(password)
            self.secret_file = open(self.secret_fp, 'r')

    @classmethod
    def _user(cls):
        for user in [user for user in psutil.users()]:
            return user if User.username == user.name \
                else None and logging.error(f'User "{User.username}" was not found.') and sys.exit()

    def sudo_test(self, fp):
        if b'SUDOER' not in check_output('sudo -S echo SUDOER'.split(), stdin=open(fp, 'r'), stderr=DEVNULL):
            self.delete_secret_files()
            logging.warning(f'Failed password attempt for {self.username}..')
        else:
            return fp

    def authenticate(self, password):
        """Password prompt provided to users that are not root."""
        attempts = 0
        while attempts != 3:
            if not password:
                fp = self.create_secret_file(Prompt.ask(f'Enter password for {self.username}'))
                if fp := self.sudo_test(fp):
                    return fp
                else:
                    attempts += 1
            else:
                fp = self.create_secret_file(password)
                if fp := self.sudo_test(fp):
                    return fp
                else:
                    attempts += 1
        fail(f'Too many failed password attempts for {self.username}.')

    def create_secret_file(self, password: str) -> str:
        """Creates secret file that only user can access, then writes the password to it"""
        fd, path = tempfile.mkstemp(prefix=f'{self.username}_', suffix='_key')
        with os.fdopen(fd, 'wb') as fp:
            fp.write(password.encode())
        logging.debug(f'Secret file "{path}" was created for "{self.username}".')
        return path

    # def get_secret(self):
    #     """Provides access to user's secret file for sudo commands."""
    #     return self.secret_file

    def delete_secret_files(self):
        """Removes all current/previous secret files from /tmp directory for user, then removes property"""
        if check_call(f'sudo -S rm {self.secret_fp}'.split(), stderr=DEVNULL, stdin=self.secret_file) == 0:
            self.secret_fp, self.secret_file = None, None
        else:
            logging.warning(Exception('FAILED_DELETING_SECRET_FILE'))

    @contextmanager
    def secret(self):
        if self.secret_file:
            try:
                yield self.secret_file
            finally:
                self.secret_file.close()

    def __repr__(self):
        return repr(f'User(username={self.username},isroot={self.isroot},terminal={self.terminal},host={self.host},'
                    f'session={self.session},pid={self.pid})')

    def __str__(self):
        r1 = f'Username: {self.username}'
        r2 = f'  Terminal  : {self.terminal}'
        r3 = f'  Host      : {self.host}'
        r4 = f'  Session   : {self.session}'
        r5 = f'  PID       : {self.pid}'
        return Fmt.m(r1, r2, r3, r4, r5)


def fail(message):
    logging.warning(message + f'  {exist_msg}'), sys.exit()

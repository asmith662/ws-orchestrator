import logging
import os
import subprocess as sub
import tempfile
from contextlib import contextmanager
from subprocess import PIPE
import sys
import time

import psutil
from rich.prompt import Prompt

from src.models.resources.mixins import Fmt

exist_msg = 'Sending shutdown signal..'


class User:
    username = u if (u := os.getlogin()) else logging.warning(Exception('ANONYMOUS_USER'))

    def __init__(self):
        self.username = name if (name := User.username) \
            else None and logging.warning(Exception('USER_NOT_FOUND')) and sys.exit()
        self.isroot = os.geteuid() == 0
        self.terminal = self.user[0].terminal
        self.host = self.user[0].host
        self.session = self._secs2time(self.user[0].started)
        self.pid = int(self.user[0].pid)

    @property
    def user(self):
        for user in [user for user in psutil.users()]:
            return user if self.username == user.name \
                       else None, logging.warning(f'User "{self.username}" was not found.')

    def __repr__(self):
        return repr(f'User(username={self.username},isroot={self.isroot},terminal={self.terminal},host={self.host},'
                    f'session={self.session},pid={self.pid}')

    def __iter__(self):
        return self

    def __next__(self, user):
        if not self.user:
            raise StopIteration
        return self

    def __str__(self):
        r1 = f'Username: {self.username}'
        r2 = f'  Terminal  : {self.terminal}'
        r3 = f'  Host      : {self.host}'
        r4 = f'  Session   : {self._session()}'
        r5 = f'  PID       : {self.pid}'
        return Fmt.m(r1, r2, r3, r4, r5)

    @classmethod
    def _secs2time(cls, seconds: int or float):
        return time.strftime("%H:%M:%S", time.gmtime(seconds))

    def _session(self):
        h, m, s = self.session.split(':')
        return f'{int(h) + int(m) / 60} hours'


class Auth:
    try_map = ['First', 'Second', 'Third', 'Fourth', 'Fifth']

    def __init__(self, pwd=None, strict=False):
        self.strict = strict
        self.user = self._user()
        if not self.user.isroot:
            self.password = self._auth(self.user, pwd, self.strict)
            self.authenticated = bool(self.user.isroot or self.password)
            self.file_descriptor, self.file_path = self._auth(self.user, pwd, self.strict)

    @classmethod
    def _auth(cls, user: User, pwd, strict):
        """Prompts user for a password, and confirms they are able to sudo.

        Creates a temporary file and changes write permissions,
        so that only the current user is capable of accessing it
        then returns the file descriptor and path.
        """
        return cls._pwd_prompt(user.name, strict) if pwd and not cls._can_sudo(pwd) else pwd

    @classmethod
    def _pwd_prompt(cls, username, strict) -> str:
        """Password prompt provided to users that are not root.

        Toggling strict will change the amount of attempts given
        for a user to enter a password that is confirmed to be
        able to sudo.
        """
        attempts = 5 if not strict else 3
        while not attempts == 0:
            if cls._can_sudo((pwd := Prompt.ask(f'Enter password for {username}:    ', password=True))):
                return pwd
            else:
                attempts -= 1
                logging.warning(f'{cls.try_map[attempts]} failed password attempt for {username}')
        fail(f'Too many failed password attempts for {username}.')

    @classmethod
    def _can_sudo(cls, pwd):
        """Sudo test.

        The provided password is used to echo the word 'confirmed'
        to standard error stream to hide its output from the terminal. If 'confirmed'
        in the output then user can sudo.
        """
        kwargs = dict(stderr=PIPE, input=pwd) if pwd else dict(stderr=PIPE)
        return "confirmed" in str(sub.run(f"sudo -S echo confirmed".split(), **kwargs).stderr)

    @staticmethod
    @contextmanager
    class SecretManager:
        def __init__(self, username, password):
            self.username = Auth.user
            self.file_descriptor, self.file_path = None, None

    def _secret_file(self):
        fd, path = tempfile.mkstemp(prefix=f'{self.user.name}_', suffix='_key')
        with os.fdopen(fd, 'wb') as fp:
            fp.write(self.pwd.encode())
        return fd, path

    def deauth(self):
        kwargs = dict(stderr=open(os.devnull, 'r'), input=open(self.file_path, 'r'))
        self.authenticated = bool(sub.run(f'sudo -S rm {self.file_path}'.split(), **kwargs).returncode != 0)
        logging.info(f'{self.user.name} is now signed-out.') if not self.authenticated \
            else logging.error(Exception('DEAUTHENTICATION_FAILED')), sys.exit()

    # def __enter__(self):
    #     logging.info(f'{self.user.name} is now authenticated.')
    #     if not self.user.isroot and (pwd := self.authenticate(self.password)):
    #         self.file, self.path = tempfile.mkstemp(prefix=f'{self.user.name}_')
    #         with os.fdopen(self.file, 'wb') as fp:
    #             fp.write(pwd.encode())
    #         self.authenticated = True

    # def pwd(self):
    #     try:
    #         return open(self.path, 'w')
    #     except FileNotFoundError:
    #         print(FileNotFoundError), logging.error(FileNotFoundError), sys.exit()
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     kwargs = dict(stderr=open(os.devnull, 'w'), input=open(self.path, 'w'))
    #     if sub.run(f'sudo -S rm {self.path}'.split(), **kwargs).returncode == 0:
    #         self.authenticated = False
    #         logging.info(f'{self.user.name} is now signed-out.')

    def __repr__(self):
        return repr(f'Auth(user=User({self.user}))')


def fail(message):
    logging.warning(message + f'  {exist_msg}'), sys.exit()

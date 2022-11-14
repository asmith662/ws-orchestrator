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
            self.secret_file = self.authenticate(password)

    @classmethod
    def _user(cls):
        for user in [user for user in psutil.users()]:
            return user if User.username == user.name \
                else None and logging.error(f'User "{User.username}" was not found.') and sys.exit()

    def sudo_test(self, path):
        if b'SUDOER' not in check_output('sudo -S echo SUDOER'.split(), stdin=open(path, 'r'), stderr=DEVNULL):
            self.delete_secret_files()
            logging.warning(f'Failed password attempt for {self.username}..')
        else:
            return path

    def authenticate(self, password):
        """Password prompt provided to users that are not root."""
        attempts = 0
        while attempts != 3:
            if not password:
                path = self.create_secret_file(Prompt.ask(f'Enter password for {self.username}'))
                if path := self.sudo_test(path):
                    return path
                else:
                    attempts += 1
            else:
                path = self.create_secret_file(password)
                if path := self.sudo_test(path):
                    return path
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

    def get_secret(self):
        """Provides access to user's secret file for sudo commands."""
        return self.secret_file

    def delete_secret_files(self):
        """Removes all current/previous secret files from /tmp directory for user, then removes property"""
        if check_call(f'sudo -S rm {self.secret_file}'.split(), stderr=DEVNULL, stdin=open(self.secret_file, 'r')) == 0:
            self.secret_file = None
        else:
            logging.warning(Exception('FAILED_DELETING_SECRET_FILE'))

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


# class Auth:
#     try_map = ['First', 'Second', 'Third', 'Fourth', 'Fifth']
#
#     def __init__(self, pwd=None, strict=False):
#         self.strict = strict
#         self.user = self._user()
#         if not self.user.isroot:
#             self.password = self._auth(self.user, pwd, self.strict)
#             self.authenticated = bool(self.user.isroot or self.password)
#             self.file_descriptor, self.file_path = self._auth(self.user, pwd, self.strict)
#
#     @staticmethod
#     @contextmanager
#     class SecretManager:
#         def __init__(self, username, password):
#             self.username = Auth.user
#             self.file_descriptor, self.file_path = None, None
#
#     def _secret_file(self):
#         fd, path = tempfile.mkstemp(prefix=f'{self.user.name}_', suffix='_key')
#         with os.fdopen(fd, 'wb') as fp:
#             fp.write(self.pwd.encode())
#         return fd, path
#
#     def deauth(self):
#         kwargs = dict(stderr=open(os.devnull, 'r'), input=open(self.file_path, 'r'))
#         self.authenticated = bool(sub.run(f'sudo -S rm {self.file_path}'.split(), **kwargs).returncode != 0)
#         logging.info(f'{self.user.name} is now signed-out.') if not self.authenticated \
#             else logging.error(Exception('DEAUTHENTICATION_FAILED')), sys.exit()

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

#     def __repr__(self):
#         return repr(f'Auth(user=User({self.user}))')
#
#
def fail(message):
    logging.warning(message + f'  {exist_msg}'), sys.exit()


@contextmanager
def secret_manager(secret_fp):
    secret = open(secret_fp, 'r')
    try:
        yield secret
    finally:
        secret.close()

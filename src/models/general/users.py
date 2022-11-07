import os
import time

import psutil

from src.models.resources.mixins import Fmt


class User:
    def __init__(self, user):
        self.name = user.name
        self.isroot = os.geteuid() == 0
        self.terminal = user.terminal
        self.host = user.host
        self.session = self._secs2time(user.started)
        self.pid = int(user.pid)

    def __repr__(self):
        return repr(f'User(name={self.name},root={self.isroot},terminal={self.terminal},host={self.host},'
                    f'session={self.session},pid={self.pid}')

    def __iter__(self):
        return self

    def __next__(self, user):
        if not user:
            raise StopIteration
        return self

    def __str__(self):
        r1 = f'User: {self.name}'
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
        return f'{int(h) + int(m)/60} hours'


class Users:
    def __init__(self):
        self.users = [User(u) for u in psutil.users()]
        self.count = len(self.users)

    def __repr__(self):
        return repr(f'Users({self.users}')

    def __str__(self):
        rows = [str(u) for u in self.users]
        return Fmt.m(*rows)

    def __iter__(self):
        return self

    def __next__(self):
        for count, user in enumerate(self.users):
            if count > len(self.users):
                raise StopIteration
            else:
                return user

    def update(self):
        self.users = [User(u) for u in psutil.users()]

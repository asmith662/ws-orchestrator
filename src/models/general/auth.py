import getpass
import logging
import os
import subprocess
import sys

from src.models.general.users import User, Users


class Auth:
    try_map = ['First', 'Second', 'Third', 'Fourth', 'Fifth']

    def __init__(self, username=None, password=None):
        self.users = Users().users
        self.username = self._user()
        self.password = None

    def __repr__(self):
        return repr(f'Auth({self.users}')

    def __enter__(self):
        pass

    @classmethod
    def _fail_log(cls, username, tries):
        logging.warning(f'{cls.try_map[tries]} failed password attempt for {username}')
        tries += 1
        return tries

    def update_users(self):
        self.users = Users().users

    def get_user(self, user):
        return user if user in self.users[user] else print('USER_NOT_FOUND') and logging.warning('USER_NOT_FOUND')


    def _auth(self, username=None, pwd=None):
        if username:
            self._pwd(pwd)
        if username := os.getlogin():
            if user := [self.get_user(user) for user in self.users]:
                pass

    def set_creds(self, username, pwd):
        if self._sudo_check(pwd):
            self.username = username
            self.password = pwd
            logging.info(f'{username} is now authenticated.')
            return True
        else:
            print(f'Your password did not mach the sudoers file for {username}.')
            return False

    def fail_counter(self, username, tries):
        if not self.set_creds(username, input(f'Enter password for {username}:    ')):
            return self._fail_log(username, tries)

    def _prompt(self, username, tries):
        while tries != 4:
            if tries := self.fail_counter(username, tries):
                return tries
        logging.warning(f'{username} entered there password incorrectly too many times.'), sys.exit()

    def _pwd(self, username, pwd=None):
        tries = 0
        if not pwd:
            tries = self._prompt(username, tries)
        else:
            self.fail_counter(username, tries)
            print(f'The password you provided did match the sudoers file.  Please try again..')
            self._prompt(username, tries)

    @classmethod
    def _sudo_check(cls, pwd):
        kwargs = dict(stdout=subprocess.PIPE, encoding="ascii")
        if pwd:
            kwargs.update(input=pwd)
        return True if "confirmed" in str(subprocess.run(f"sudo -S echo confirmed".split(), **kwargs).stdout) else False


# Global Arguments
DONT_ASK_TO_SAVE_PASSWORD = False
PASSWORD_SAVED = False
CAN_SUDO = False
IS_ROOT = False


def pwd_check(pwd: str = None) -> str:
    if not pwd or pwd == '':
        return get_pwd()
    else:
        return pwd


def get_pwd():
    if not (IS_ROOT or CAN_SUDO):
        return pwd_prompt()
    else:
        return Password


# def custom_getpass(prompt='Password: ', stream=None):
#     if not stream:
#         stream = sys.stderr
#     print("This is a custom message to the user.", file=stream)
#     # noinspection PyProtectedMember
#     return getpass._raw_input(prompt, stream)


def is_root():
    global IS_ROOT
    IS_ROOT = (os.geteuid() == 0)
    return IS_ROOT


def can_sudo(pwd: str = None) -> bool:
    global CAN_SUDO
    if is_root():
        print('Root user detected.')
        CAN_SUDO = True
    args = f"sudo -S echo AUTHENTICATED".split()
    kwargs = dict(stdout=subprocess.PIPE, encoding="ascii")
    if pwd:
        kwargs.update(input=pwd)
    cmd = subprocess.run(args, **kwargs)
    CAN_SUDO = "AUTHENTICATED" in str(cmd.stdout)
    return CAN_SUDO


def pwd_prompt():
    pwd = getpass.getpass(prompt=f'[sudo] password for {getpass.getuser()}: ')
    if can_sudo(pwd):
        if not DONT_ASK_TO_SAVE_PASSWORD:
            save_prompt(pwd)
        return pwd
    else:
        pwd_prompt()


def save_prompt(pwd) -> None:
    global Password, PASSWORD_SAVED
    save = input('Save password for future command that require sudo? \'y\' | \'n\'\n')
    if save == 'y' or save == 'n':
        if save == 'y':
            if PASSWORD_SAVED:
                overwrite_prompt(pwd)
        else:
            if not DONT_ASK_TO_SAVE_PASSWORD:
                ask_again_prompt()
    else:
        save_prompt(pwd)


def ask_again_prompt() -> None:
    global DONT_ASK_TO_SAVE_PASSWORD
    ask = input('Don\'t ask to save password again? \'y\' | \'n\'\n')
    if ask == 'y' or ask == 'n':
        if ask == 'y':
            DONT_ASK_TO_SAVE_PASSWORD = True
    else:
        ask_again_prompt()


def overwrite_prompt(pwd: str) -> None:
    global Password, PASSWORD_SAVED
    overwrite = input('Overwrite existing password? \'y\' | \'n\'\n')
    if overwrite == 'y' or overwrite == 'n':
        if overwrite == 'y':
            Password = pwd
            PASSWORD_SAVED = True
    else:
        overwrite_prompt(pwd)

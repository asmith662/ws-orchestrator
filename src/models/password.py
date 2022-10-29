import getpass
import os
import subprocess
import sys

# Global Variables
Password = ''

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


def custom_getpass(prompt='Password: ', stream=None):
    if not stream:
        stream = sys.stderr
    print("This is a custom message to the user.", file=stream)
    # noinspection PyProtectedMember
    return getpass._raw_input(prompt, stream)


def is_root():
    global IS_ROOT
    IS_ROOT = (os.geteuid() == 0)
    return IS_ROOT


def can_sudo(pwd: str = None) -> bool:
    global CAN_SUDO
    if is_root():
        CAN_SUDO = True
    args = f"sudo -S echo OK".split()
    kwargs = dict(stdout=subprocess.PIPE, encoding="ascii")
    if pwd:
        kwargs.update(input=pwd)
    cmd = subprocess.run(args, **kwargs)
    CAN_SUDO = "OK" in str(cmd.stdout)
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
    save = input('Save password for future commands that require sudo? \'y\' | \'n\'\n')
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

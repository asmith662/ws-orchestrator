import getpass
import subprocess

# Global Variables
Password = ''

# Global Arguments
DONT_ASK_TO_SAVE_PASSWORD = False
PASSWORD_SAVED = False
CAN_SUDO = False
IS_ROOT = False


def get_pass():
    pwd = getpass.getpass(prompt='[sudo] password for {user}: ')
    if can_sudo(pwd):
        if not DONT_ASK_TO_SAVE_PASSWORD:
            save_prompt(pwd)
        return pwd
    else:
        get_pass()


def save_prompt(pwd):
    global Password, DONT_ASK_TO_SAVE_PASSWORD
    save = input('Save password for future commands that require sudo? \'y\' | \'n\'\n')
    if save == 'y' or save == 'n':
        if save == 'y':
            Password = pwd
        elif save == 'n':
            ask = input('Don\'t ask to save password again? \'y\' | any key to cancel\n')
            if ask == 'y':
                DONT_ASK_TO_SAVE_PASSWORD = True
    else:
        save_prompt(pwd)


def can_sudo(pwd: str = Password) -> bool:
    args = f" echo {pwd} | sudo -S -k iwconfig".split()
    kwargs = dict(stdout=subprocess.PIPE, encoding="ascii")
    if pwd:
        kwargs.update(input=pwd)
    print(args)
    cmd = subprocess.run(args, **kwargs)
    print(cmd.stdout)
    return "OK" in str(cmd.stdout)

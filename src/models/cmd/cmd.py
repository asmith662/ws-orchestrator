import logging
import os
import subprocess
from subprocess import run

import sh

from src.models.password import can_sudo, get_pass, DONT_ASK_TO_SAVE_PASSWORD, Password


def sudo_cmd(cmd: str) -> bool:
    return 'sudo' in cmd


def format_cmd(cmd: str, pwd: str = None) -> tuple:
    args = cmd.split()
    kwargs = dict(stdout=subprocess.PIPE, encoding="ascii")
    if pwd and can_sudo():
        kwargs.update(input=pwd)
    return args, kwargs,


def get_cmd(cmd: str, pwd: str = None) -> tuple:
    if 'sudo' in cmd:
        root = os.geteuid() == 0
        if not (root and pwd):
            pwd = get_pass()
            return format_cmd(cmd, pwd)
        else:
            if DONT_ASK_TO_SAVE_PASSWORD:
                return format_cmd(cmd, pwd)
            elif can_sudo(pwd):
                return format_cmd(cmd, pwd)
    else:
        return format_cmd(cmd)


def run_cmd(cmd: str, pwd: str = None):
    out = os.system(f"echo {pwd} | sudo -S {cmd}")
    print(out)
    # args, kwargs = get_cmd(cmd, pwd)
    # cmd = subprocess.run(args, **kwargs)
    # print(cmd)


def stream_cmd(cmd: str, pwd: str = Password) -> str:
    # if 'sudo' in cmd and pwd != '':
    # args = cmd
    pswd = get_pass()
    # return os.popen(cmd).read()
    p = subprocess.Popen(['sudo', '-S', cmd], stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    err = None
    try:
        out, err = p.communicate(input=(pswd + '\n').encode(), timeout=5)
        return out.decode()
    except subprocess.TimeoutExpired:
        logging.warning("Killing processes due to:", err.decode())
        p.kill()


def stream_cmd_hidden(cmd: str):
    pswd = get_pass()
    p = subprocess.Popen(['sudo', '-S', cmd], stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    try:
        out, err = p.communicate(input=(pswd + '\n').encode(), timeout=5)
        return out, err,
    except subprocess.TimeoutExpired:
        p.kill()


# def with_sudo():
#     with sh.contrib.sudo:
#         print(sudo.ls("/root"))
#
# def check_return_code(process) -> str:
#     if process.returncode == 0:
#         return process.stdout.decode()
#     else:
#         return 'Error Message:' + process.stderr.decode()
#
#
# async def run_cmd(cmd: str, args: str, input_data: str = None) -> str or None:
#     if not input_data:
#         process = run([cmd, args], capture_output=True)
#     else:
#         process = run([cmd, args], capture_output=True, input=input_data.encode())
#     return check_return_code(process)
#
#
# async def run_shell_cmd(cmd: str) -> str:
#     return check_return_code(run(cmd, shell=True))
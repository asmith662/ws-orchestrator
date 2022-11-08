import logging
import os
import re
import subprocess
import sys
from abc import ABC, abstractmethod


class Executor(ABC):
    cprompt = ["cmd", "/c"]
    pshell = ["pwsh", "-Command"]
    bash = ['bash', '-c']

    @abstractmethod
    def run(self, cmd):
        """Abstract method to run command"""


class Option:
    def __init__(self):
        pass


class Cmd(Option):
    def __init__(self, cmd, pwd=None, timeout=None, capture_output=True, encoding='utf-8'):
        super().__init__()
        self.cmd = cmd
        self.sudo = True if 'sudo' in cmd else False
        self.timeout = timeout
        self.capture_output = capture_output
        self.encoding = encoding
        self.stout = self.run(self.cmd, self._options(pwd))

    @staticmethod
    def run(cmd, options):
        try:
            return subprocess.run(cmd.split(), **options).stdout
        except subprocess.CalledProcessError as exc:
            m = f'Process failed due to unsuccessful return code. [{exc.returncode}]\n{exc}'
            logging.warning(m)
        except subprocess.TimeoutExpired as exc:
            logging.warning(f'Process timed out.\n{exc}\nSending shutdown signal..'), sys.exit()

    def _options(self, pwd):
        if not self.sudo:
            return dict(timeout=self.timeout, capture_output=self.capture_output, encoding=self.encoding,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if pwd:
            return dict(input=pwd, timeout=self.timeout, capture_output=self.capture_output, encoding=self.encoding,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            m = f'Missing password for sudo command:\n{self.cmd}\nSending shutdown signal..'
            print(m), logging.warning(m), sys.exit()


class AsyncCmd(Option):
    def __init__(self, pwd, cmd, timeout=None):
        super().__init__()
        self.cmd = cmd
        self.timeout = timeout

    def run(self, pwd, cmd, regex):
        monitors, interfaces = [], {}
        proc = None
        try:
            proc = subprocess.Popen(cmd.split(),
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=open(os.devnull, 'w'))
        except OSError:
            logging.warning(f'Could not execute:\n"{self.cmd}"\nSending shutdown signal..')
        for line in proc.communicate(pwd.encode())[0].split('\n'.encode()):
            if len(line) == 0:
                continue  # Isn't an empty string
            if line[0] != ' ':  # Doesn't start with space
                wired_search = re.search(rf'{regex}'.encode(), line)
                if not wired_search:  # Isn't wired
                    iface = line[:line.find(' '.encode())]
                    if 'Mode:Monitor'.encode() in line:
                        monitors.append(iface)
                    elif 'IEEE 802.11'.encode() in line:
                        if "ESSID:\"".encode() in line:
                            interfaces[iface] = 1
                        else:
                            interfaces[iface] = 0

    @staticmethod
    def kill(process: subprocess.Popen, exception: Exception, cmd: str, stderr: bytes or None) -> None:
        logging.warning(f"{exception} while running {cmd}")
        if stderr:
            logging.warning("stderr:", stderr.decode())
        logging.warning("Killing process...")
        process.kill()


def run_cmd2(cmd1: [str], cmd2: [str] or None, pwd: str = Password) -> None:
    pwd = pwd_check(pwd)
    s1, s2 = sudo(cmd1), sudo(cmd2)
    print(s1, s2)
    p1 = subprocess.Popen(s1, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, stdin=subprocess.PIPE, )
    p2 = subprocess.Popen(s2, stdout=subprocess.PIPE, stdin=p1.stdout, )
    e1, e2 = None, None
    try:
        o1, e1 = p1.communicate(input=pwd.encode())
        o2, e2 = p2.communicate()
        print(o1.decode(), e1.decode())
        print(o2.decode(), e2.decode())
    except Exception as e:
        kill(p1, e, ' '.join(s1), e1)


def run_background_cmd(cmd: str, pwd: str = Password, timeout: int = 5):
    pwd = pwd_check(pwd)
    p = subprocess.Popen(sudo(cmd), stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    err = None
    try:
        out, err = p.communicate(input=(pwd + '\n').encode(), timeout=timeout)
        return out.decode()
    except subprocess.TimeoutExpired as expired:
        kill(p, expired, cmd, err)
    except Exception as e:
        kill(p, e, cmd, err)


# Not sure if this one will work or not, but leaving it for now
def stream_cmd(cmd: str, pwd: str = Password):
    pwd = pwd_check(pwd)
    p = subprocess.Popen(sudo(cmd), stderr=subprocess.STDOUT, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                         universal_newlines=True, bufsize=0)
    out, err = None, None
    try:
        while True:
            p.stdin.write(pwd)
            out = p.stdout.readline()
            if len(out) == 0 and p.poll() is not None:
                break
            if out:
                print(out.strip())
        rc = p.poll()
        return rc
    except Exception as e:
        kill(p, e, cmd, err)




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
# async def run_cmd(command: str, args: str, input_data: str = None) -> str or None:
#     if not input_data:
#         process = run([command, args], capture_output=True)
#     else:
#         process = run([command, args], capture_output=True, input=input_data.encode())
#     return check_return_code(process)
#
#
# async def run_shell_cmd(command: str) -> str:
#     return check_return_code(run(command, shell=True))
#
# def format_cmd(command: str, pwd: str = None) -> tuple:
#     args = command.split()
#     kwargs = dict(stdout=subprocess.PIPE, encoding="ascii")
#     if pwd and can_sudo():
#         kwargs.update(input=pwd)
#     return args, kwargs,
#
#
# def get_cmd(command: str, pwd: str = None) -> tuple:
#     if is_sudo_cmd(command):
#         root = os.geteuid() == 0
#         if not (root and pwd):
#             pwd = pwd_prompt()
#             return format_cmd(command, pwd)
#         else:
#             if DONT_ASK_TO_SAVE_PASSWORD:
#                 return format_cmd(command, pwd)
#             elif can_sudo(pwd):
#                 return format_cmd(command, pwd)
#     else:
#         return format_cmd(command)
#
#
# def run_cmd(command: str, pwd: str = None):
#     return f"echo {pwd} | sudo -S {command}"

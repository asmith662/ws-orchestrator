import logging
import subprocess

from src.models.password import Password, pwd_check


# Wrapper for all cmds
def execute(cmd: str):
    if is_sudo_cmd(cmd):
        pass
    else:
        pass


def sudo(cmd: str) -> list:
    return ['sudo', '-S', cmd]


def is_sudo_cmd(cmd: str) -> bool:
    return 'sudo' in cmd


def run_cmd(cmd: str, pwd: str = Password) -> str:
    pwd = pwd_check(pwd)
    p = subprocess.Popen(sudo(cmd), stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=False)
    err = None
    try:
        out, err = p.communicate(input=(pwd + '\n').encode())
        return out.decode()
    except Exception as e:
        kill(p, e, cmd, err)


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
    p = subprocess.Popen(sudo(cmd), stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
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


def kill(process: subprocess.Popen, exception: Exception, cmd: str, stderr: bytes or None) -> None:
    logging.warning(f"{exception} while running {cmd}")
    if stderr:
        logging.warning("stderr:", stderr.decode())
    logging.warning("Killing process...")
    process.kill()

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
#
# def format_cmd(cmd: str, pwd: str = None) -> tuple:
#     args = cmd.split()
#     kwargs = dict(stdout=subprocess.PIPE, encoding="ascii")
#     if pwd and can_sudo():
#         kwargs.update(input=pwd)
#     return args, kwargs,
#
#
# def get_cmd(cmd: str, pwd: str = None) -> tuple:
#     if is_sudo_cmd(cmd):
#         root = os.geteuid() == 0
#         if not (root and pwd):
#             pwd = pwd_prompt()
#             return format_cmd(cmd, pwd)
#         else:
#             if DONT_ASK_TO_SAVE_PASSWORD:
#                 return format_cmd(cmd, pwd)
#             elif can_sudo(pwd):
#                 return format_cmd(cmd, pwd)
#     else:
#         return format_cmd(cmd)
#
#
# def run_cmd(cmd: str, pwd: str = None):
#     return f"echo {pwd} | sudo -S {cmd}"

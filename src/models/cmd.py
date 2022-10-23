import os
from subprocess import run


def check_return_code(process) -> str:
    if process.returncode == 0:
        return process.stdout.decode()
    else:
        return 'Error Message:' + process.stderr.decode()


async def run_cmd(cmd: str, args: str, input_data: str = None) -> str or None:
    if not input_data:
        process = run([cmd, args], capture_output=True)
    else:
        process = run([cmd, args], capture_output=True, input=input_data.encode())
    return check_return_code(process)


async def run_shell_cmd(cmd: str) -> str:
    return check_return_code(run(cmd, shell=True))


def stream_cmd(cmd: str) -> str:
    return os.popen(cmd).read()


def stream_cmd_hidden(cmd: str):
    return os.popen(cmd)

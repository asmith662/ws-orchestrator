from subprocess import run
from typing import Dict


async def execute(cmd: str, args: str, input_data: str = None) -> str or None:
    if not input_data:
        process = run([cmd, args], capture_output=True)
    else:
        process = run([cmd, args], capture_output=True, input=input_data.encode())

    if process.returncode == 0:
        stdout = process.stdout.decode()

        if stdout:
            return stdout

    else:
        print(f'Error while executing the command {cmd} with rgs: {args}')

        msg = process.stderr.decode()
        if msg:
            print(f'Error Message: {msg}')

        return None


async def echo(args):
    return await execute('echo', args)


async def cat(args):
    return await execute('echo', args, args)

import logging
import os
import re
import subprocess as sub
import sys
import tempfile


def testme(pwd: str, cmd: str):
    """Creates a secure temp pass file which allows sudo commands to be tested then the file is deleted."""

    # creating tempfile and writing password to it
    fd, path = tempfile.mkstemp(prefix=f'{os.getlogin()}_', suffix='_key')
    with os.fdopen(fd, 'wb') as fp:
        fp.write(pwd.encode())

    #                                               Your Code Here:
    # ---------------------------------------------------START----------------------------------------------------------

    # ----------------------------------------------------END-----------------------------------------------------------

    # deleting tempfile and printing result
    result = sub.run(f'sudo -S rm {path}'.split(), **dict(stderr=sub.DEVNULL, input=open(path, 'r').read().encode())
                     ).returncode
    print('Success' if result == 0 else f'Failure with return code: {result}')
    

class Cmd:
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
            return sub.run(cmd.split(), **options).stdout
        except sub.CalledProcessError as exc:
            m = f'Process failed due to unsuccessful return code. [{exc.returncode}]\n{exc}'
            logging.warning(m)
        except sub.TimeoutExpired as exc:
            logging.warning(f'Process timed out.\n{exc}\nSending shutdown signal..'), sys.exit()

    def _options(self, pwd):
        if not self.sudo:
            return dict(timeout=self.timeout, capture_output=self.capture_output, encoding=self.encoding,
                        stdout=sub.PIPE, stderr=sub.PIPE)
        if pwd:
            return dict(input=pwd, timeout=self.timeout, capture_output=self.capture_output, encoding=self.encoding,
                        stdout=sub.PIPE, stderr=sub.PIPE)
        else:
            m = f'Missing password for sudo command:\n{self.cmd}\nSending shutdown signal..'
            print(m), logging.warning(m), sys.exit()


class AsyncCmd:
    def __init__(self, pwd, cmd, timeout=None):
        super().__init__()
        self.cmd = cmd
        self.timeout = timeout

    def run(self, pwd, cmd, regex):
        monitors, interfaces = [], {}
        proc = None
        try:
            proc = sub.Popen(cmd.split(), stdin=sub.PIPE, stdout=sub.PIPE, stderr=open(os.devnull, 'w'))
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
    def kill(process: sub.Popen, exception: Exception, cmd: str, stderr: bytes or None) -> None:
        logging.warning(f"{exception} while running {cmd}")
        if stderr:
            logging.warning("stderr:", stderr.decode())
        logging.warning("Killing process...")
        process.kill()


def check():
    """Check if aircrack-ng is compatible."""
    assert b'1.6' in sub.check_output(['aircrack-ng', '-v'])

# def run_cmd2(cmd1: [str], cmd2: [str] or None, pwd: str = Password) -> None:
#     pwd = pwd_check(pwd)
#     s1, s2 = sudo(cmd1), sudo(cmd2)
#     print(s1, s2)
#     p1 = sub.Popen(s1, stderr=sub.STDOUT, stdout=sub.PIPE, stdin=sub.PIPE, )
#     p2 = sub.Popen(s2, stdout=sub.PIPE, stdin=p1.stdout, )
#     e1, e2 = None, None
#     try:
#         o1, e1 = p1.communicate(input=pwd.encode())
#         o2, e2 = p2.communicate()
#         print(o1.decode(), e1.decode())
#         print(o2.decode(), e2.decode())
#     except Exception as e:
#         kill(p1, e, ' '.join(s1), e1)
#
#
# def run_background_cmd(cmd: str, pwd: str = Password, timeout: int = 5):
#     pwd = pwd_check(pwd)
#     p = sub.Popen(sudo(cmd), stderr=sub.PIPE, stdout=sub.PIPE, stdin=sub.PIPE)
#     err = None
#     try:
#         out, err = p.communicate(input=(pwd + '\n').encode(), timeout=timeout)
#         return out.decode()
#     except sub.TimeoutExpired as expired:
#         kill(p, expired, cmd, err)
#     except Exception as e:
#         kill(p, e, cmd, err)


# Not sure if this one will work or not, but leaving it for now
# def stream_cmd(cmd: str, pwd: str = Password):
#     pwd = pwd_check(pwd)
#     p = sub.Popen(sudo(cmd), stderr=sub.STDOUT, stdout=sub.PIPE, stdin=sub.PIPE,
#                          universal_newlines=True, bufsize=0)
#     out, err = None, None
#     try:
#         while True:
#             p.stdin.write(pwd)
#             out = p.stdout.readline()
#             if len(out) == 0 and p.poll() is not None:
#                 break
#             if out:
#                 print(out.strip())
#         rc = p.poll()
#         return rc
#     except Exception as e:
#         kill(p, e, cmd, err)

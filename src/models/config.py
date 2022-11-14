import logging
import os
import re
from logging.handlers import RotatingFileHandler
from subprocess import Popen, DEVNULL, PIPE, run


class Startup:
    def __init__(self):
        self.logger()
        self.cleanup()
        self.banner()
        self.greeting()

    @staticmethod
    def logger():
        try:
            log_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../ws-orchestrator.log'))
            logging.basicConfig(
                handlers=[
                    RotatingFileHandler(
                        log_path,
                        maxBytes=25000000,
                        backupCount=5
                    )
                ],
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s: %(message)s',
                datefmt='%d-%b-%y %H:%M:%S'
            )
            logging.info('Starting ws-orchestrator...')
        except Exception as e:
            print('While configuring logger, error:', e)

    @staticmethod
    def cleanup():
        user = os.getlogin()
        with Popen(f'ls /tmp'.split(), stderr=DEVNULL, stdout=PIPE) as proc_launch:
            files = proc_launch.communicate()[0].decode().split('\n')
        if fps := ' '.join(
                [f for f in ['/tmp/' + f for f in files] if re.search(f'^/tmp/' + user + '[a-z0-9_]+_key$', f)]):
            return True and logging.debug(f'Removed "{files}" leftover from previous execution') \
                if run(f'rm {fps}'.split()).returncode == 0 \
                else False and logging.warning('Failed to remove existing password files.')

    @staticmethod
    def banner():
        return print("""
░██╗░░░░░░░██╗░██████╗░░░░░░░█████╗░██████╗░░█████╗░██╗░░██╗███████╗░██████╗████████╗██████╗░░█████╗░████████╗░█████╗░██████╗░
░██║░░██╗░░██║██╔════╝░░░░░░██╔══██╗██╔══██╗██╔══██╗██║░░██║██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗
░╚██╗████╗██╔╝╚█████╗░█████╗██║░░██║██████╔╝██║░░╚═╝███████║█████╗░░╚█████╗░░░░██║░░░██████╔╝███████║░░░██║░░░██║░░██║██████╔╝
░░████╔═████║░░╚═══██╗╚════╝██║░░██║██╔══██╗██║░░██╗██╔══██║██╔══╝░░░╚═══██╗░░░██║░░░██╔══██╗██╔══██║░░░██║░░░██║░░██║██╔══██╗
░░╚██╔╝░╚██╔╝░██████╔╝░░░░░░╚█████╔╝██║░░██║╚█████╔╝██║░░██║███████╗██████╔╝░░░██║░░░██║░░██║██║░░██║░░░██║░░░╚█████╔╝██║░░██║
░░░╚═╝░░░╚═╝░░╚═════╝░░░░░░░░╚════╝░╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝╚══════╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝       
        """)

    @staticmethod
    def greeting():
        user = 'root' if os.geteuid() == 0 else os.getlogin()
        return print(f"""
Welcome "{user}". This tool implements the Ng suite for various wireless attack simulations. 
Non-root users must first authenticate.\n""")


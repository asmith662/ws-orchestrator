import asyncio
import functools
import itertools
import logging
import os
import re
import subprocess
from subprocess import Popen, PIPE, DEVNULL
import tempfile
import uuid
from abc import abstractmethod

import stringcase


class DocOpt:
    def __init__(self, option_description):
        self.data = self.parse(option_description)
        self.description = self.data['desc']
        self.arg_types = self.data['arg_types']
        self.arg_type = self.data['arg_type']
        self.arg = self.data['arg']
        self.value = None if self.data['default'] is False and self.arg else self.data['default']
        self.keys = self.data['keys']
        self.key = self.data['key']
        self.aliases = self.data['aliases']
        self.alias = self.data['alias']
        self.options = {self.key: self.arg}

    @classmethod
    def parse(cls, option_description):
        option_description = option_description.strip().split(' : ')
        opt, desc = option_description[0], option_description[1]
        arg_types = a[0][1:-1] and (opt := re.sub('[ =]<.+>', '', opt)) if (a := re.findall('<.+>', opt)) else None
        arg_type = arg_types[0] if arg_types else None
        arg = True if arg_types else False
        default = None
        if arg and (defaults := re.findall('default: ([A-Za-z0-9 ]+)', desc, flags=re.I)):
            default = defaults[0].strip()
        keys = [k for k in re.findall('--[A-Za-z0-9-]+|-[A-Za-z0-9-]+', opt)]
        key = keys[0] if keys else None
        aliases = [key for key in keys[1:] if len(keys) > 1]
        alias = aliases[0] if aliases else None
        return {'desc': desc, 'arg_types': arg_types, 'arg_type': arg_type, 'arg': arg, 'default': default,
                'keys': keys, 'key': key, 'aliases': aliases, 'alias': alias}

    def options(self):
        return self.options


class Doc:
    """
        TO DO:
            - populate meta dict and return it along with kwargs
    """
    redir = '^(-|--)\\w+'
    sect = '(?<=\n).+(?=\n)'

    def __init__(self, docstring):
        self.docstring = docstring
        self.options = {DocOpt(o).key: DocOpt(o).arg for o in self._split(docstring) if o.startswith('-')}
        self.args = self.args(docstring)
        self.kwargs = self.kwargs(docstring)
        # self.dict = {self.args: self.kwargs}
        # print({self.args: self.kwargs})

    @classmethod
    def _split(cls, docstring):
        split = re.split(r'\n *(<\S+?>|-\S+?)', docstring)[1:]
        return [s1 + s2 for s1, s2 in zip(split[::2], split[1::2])]

    @staticmethod
    def args(docstring):
        sections = [s.strip() for s in re.findall(Doc.sect, docstring)]
        usage = [s for s in sections if re.search(r'^[U|u]sage:\s', s)][0]
        section, name, args = usage.replace('[options] ', '').split(' ', 2)
        return [a[1:-1] for a in re.findall(r'<.+>|[.+]', args)]

    @staticmethod
    def kwargs(docstring):
        sections = [s.strip() for s in re.findall(Doc.sect, docstring)]
        meta, kwargs = [], []
        for row, opt in enumerate([s for s in sections if re.search(Doc.redir, s)]):
            cmds = opt.split(' : ')
            cmd, desc = cmds[0].strip(), cmds[1]
            arg = a[0][1:-1] if (a := re.findall('<.+>', cmd)) else None
            key_type = ktype and (cmd := re.sub('-\\w+$', '', cmd)) \
                if (ktype := re.search(Doc.redir + '-', cmd)) else None
            cmd = re.sub('((\\s|=)<.+>|(\\s|=)[.+])', '', cmd)

            if re.search(Doc.redir + '\\sor\\s', cmd):
                kwargs += [{kwarg: arg} for kwarg in list(cmd.split(' or '))]
                for kwarg in list(cmd.split(' or ')):
                    kwargs += [{kwarg: arg}]
                    # meta += [{k: args, 'type': key_type, 'description': desc}]
            else:
                kwargs += [{cmd: arg}]
        return kwargs


class Option:
    """Represents a single option (e.g, -e)."""

    def __init__(self, usage, word=None, value=None, logger=None):
        """Set option parameters."""
        self.usage = usage
        self.word = word
        self.logger = logger
        self.value = value
        keys = usage.keys()
        self.is_short = Option.short(word) in keys
        self.is_long = Option.long(word) in keys
        self.expects_args = bool(usage[self.formatted])
        self.logger.debug(f"Parsing option {self.word}:{self.value}")

    @property
    @functools.lru_cache()
    def formatted(self):
        """Format given option according to definition."""
        result = (Option.short(self.word)
                  if self.is_short else Option.long(self.word))

        if self.usage.get(result):
            return result

        sword = self.word.replace('_', '-')
        return Option.short(sword) if self.is_short else Option.long(sword)

    @staticmethod
    def long(word):
        """Extract long format option."""
        # match = re.search('^[[A-Za-z0-9]+-]*', word)
        return '--' + word

    @staticmethod
    def short(word):
        """Extract short format option."""
        return '-' + word

    @property
    def parsed(self):
        """Returns key, value if value is required."""
        if self.expects_args:
            return self.formatted, str(self.value)
        return self.formatted,

    def __repr__(self):
        return f"Option(parsed=<{self.parsed}>,is_short={self.is_short},expects_args={self.expects_args})"


class Executor:
    """Abstract class interface to a shell command."""

    def __init__(self):
        """Set docstring."""
        if not self.__doc__:
            self.__doc__ = self.helpstr
        self.uuid = uuid.uuid4().hex
        self.called = False
        self.execn = 0
        self.logger = logging.getLogger(self.__class__.__name__)
        self.proc = None
        self.meta = {}
        if self.requires_tempfile:
            self.tempfile = tempfile.NamedTemporaryFile()
        elif self.requires_tempdir:
            self.tempdir = tempfile.TemporaryDirectory()

    @property
    @abstractmethod
    def requires_tempfile(self):
        """Synchronous mode."""

    @property
    @abstractmethod
    def requires_tempdir(self):
        """Synchronous mode."""

    @property
    @abstractmethod
    def command(self):
        """Specify command to execute."""

    @property
    @functools.lru_cache()
    def helpstr(self):
        """Extract help string for current command."""
        helpcmd = f'{self.command} 2>&1; echo'
        return subprocess.check_output(helpcmd, shell=True).decode()

    @property
    @functools.lru_cache()
    def usage(self):
        """Extract usage from a specified command.

        This is useful if usage not defined in subclass, but it is recommended
        to define them there.
        """
        return Doc(self.__doc__).options

    def _run(self, *args, **kwargs):
        """Check command usage and execute it.

        If self.sync is defined, it will return process call output,
        and launch it blockingly.

        Otherwise it will call asyncio.create_subprocess_exec()
        """
        self.logger.debug(f"{self.__class__.__name__} options: {kwargs}")

        options = list((Option(self.usage, a, v, self.logger) for a, v in kwargs.items()))
        self.logger.debug(f"Got options: {options}")
        opts = ['sudo', '-S', self.command] + list(args) + list(itertools.chain(*(o.parsed for o in options)))

        self.logger.debug(f"Running command: {opts}")
        return opts

    async def run(self, *args, **kwargs):
        """Run asynchronously."""
        opts = self._run(*args, **kwargs)
        # pwd = subprocess.Popen(shlex.split('cat sudo.txt'), stdout=subprocess.PIPE)
        # fd, path = tempfile.mkstemp()
        # try:
        #     with os.fdopen(fd, 'wb') as f:
        #         f.write(b'Af4Tf2Dp!')
        #
        #     print(open(path, 'r').read())
        path = '/temp'
        self.proc = await asyncio.create_subprocess_exec(
            *opts,
            stdin=open(path, 'r'),
            stdout=subprocess.PIPE,
            stderr=open(os.devnull, 'w'))
            # pwd.stdout.close()

        # finally:
        #     subprocess.run('')
        #     os.remove(path)
        #     return self.proc

    def __call__(self, *args, **kwargs):
        self.run_args = args, kwargs
        return self

    def __aiter__(self):
        """Defines us as an async iterator."""
        return self

    async def __anext__(self):
        """Get the next result batch."""
        if not self.called:
            self.called = True
            self.proc = await self.run(*self.run_args[0], **self.run_args[1])

        if not self.running:
            raise StopAsyncIteration

        return await self.results

    @property
    def running(self):
        return self.proc.returncode is None

    async def readlines(self):
        """Return lines as per proc.communicate, non-empty ones."""
        return [a for a in (await self.proc.communicate())[0].split(b'\n') if a != b'']

    @property
    async def results(self):
        return [self.proc]

    async def __aexit__(self, *args, **kwargs):
        """Clean up conext manager."""
        if self.requires_tempfile:
            self.tempfile.__exit__(*args, **kwargs)
        elif self.requires_tempdir:
            self.tempdir.__exit__(*args, **kwargs)
        self.proc.kill()

    async def __aenter__(self):
        """Create temporary directories and files if required."""
        if self.requires_tempfile:
            self.tempfile.__enter__()
        elif self.requires_tempdir:
            self.tempdir.__enter__()
        return self


def stc(command):
    """Convert snake case to camelcase in class format."""
    return stringcase.pascalcase(command.replace('-', '_'))


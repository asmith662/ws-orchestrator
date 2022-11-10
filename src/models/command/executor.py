import asyncio
import logging
import subprocess
import functools
import itertools
import tempfile
import uuid
from abc import abstractmethod
import stringcase

from src.models.command.doc import Doc, DocOpt

logging.basicConfig(level=logging.INFO)


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
        return f"--{word}"

    @staticmethod
    def short(word):
        """Extract short format option."""
        return f"-{word}"

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
        self.logger.debug(f"Parsing options: {kwargs}")
        options = list((Option(self.usage, a, v, self.logger) for a, v in kwargs.items()))
        self.logger.debug(f"Got options: {options}")
        opts = [self.command] + list(args) + list(itertools.chain(*(o.parsed for o in options)))

        self.logger.debug(f"Running command: {opts}")
        return opts

    async def run(self, *args, **kwargs):
        """Run asynchronously."""
        opts = self._run(*args, **kwargs)
        self.proc = await asyncio.create_subprocess_exec(
            *opts,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        return self.proc

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
        com = await self.proc.communicate()
        return [a for a in com[0].split(b'\n') if a]

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

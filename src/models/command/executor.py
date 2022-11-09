import asyncio
import functools
import itertools
import logging
import re
import subprocess
import tempfile
import uuid
from abc import abstractmethod

import stringcase
from pyrcrack.executor import Option


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
        helpcmd = '{} 2>&1; echo'.format(self.command)
        return subprocess.check_output(helpcmd, shell=True).decode()

    @property
    @functools.lru_cache()
    def usage(self):
        """Extract usage from a specified command.

        This is useful if usage not defined in subclass, but it is recommended
        to define them there.
        """

        opt = parse_defaults(self.__doc__)
        for a in opt:
            print(a)
        # return dict({a.short or a.long: bool(a.argcount) for a in opt})
        return opt

    def _run(self, *args, **kwargs):
        """Check command usage and execute it.

        If self.sync is defined, it will return process call output,
        and launch it blockingly.

        Otherwise it will call asyncio.create_subprocess_exec()
        """
        self.logger.debug("Parsing options: %s", kwargs)
        options = list(
            (Option(self.usage, a, v, self.logger) for a, v in kwargs.items()))
        self.logger.debug("Got options: %s", options)

        opts = [self.command] + list(args) + list(
            itertools.chain(*(o.parsed for o in options)))

        self.logger.debug("Running command: %s", opts)
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




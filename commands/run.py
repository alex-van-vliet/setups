import sys
from contextlib import contextmanager
from os import makedirs, chdir
from pathlib import Path

from commands.command import Command
from helpers.setups import setup as setup_fun


class RunCommand(Command):
    name = "run"
    help = "run a setup"

    def setup_parser(self, parser):
        """
        Setup the command parser
        :param parser: The parser
        """
        parser.add_argument('setup', help='the setup to run')
        parser.add_argument('directory', help='where to run the setup', default='.', nargs='?')

    def __call__(self, setup: str, directory: str, **kwargs):
        """
        Run the run command
        :param setup: The name of the setup
        :param kwargs: The arguments
        :return: The exit code of the commands: 0 if successful, 1 if lexer error, 2 if parser error,
                 more if another error
        """
        destination = Path(directory).resolve()
        makedirs(destination, exist_ok=True)

        @contextmanager
        def cd(path):
            cwd = Path.cwd()
            try:
                chdir(path)
                yield path
            finally:
                chdir(cwd)

        with cd(destination):
            return setup_fun(setup)

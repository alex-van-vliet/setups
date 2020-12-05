from argparse import REMAINDER
from subprocess import Popen
from typing import List, TYPE_CHECKING

from helpers.commands.abstract_command import AbstractCommand

if TYPE_CHECKING:
    from helpers.runner import Runner


class Command(AbstractCommand):
    name = 'command'
    description = 'run a command'

    def setup_parser(self, parser):
        """
        Setup the parser
        """
        parser.add_argument('command', nargs=REMAINDER)

    def __call__(self, runner: 'Runner', command: List[str], **kwargs):
        """
        Call the command
        :param runner: The runner
        :param command: The command
        """
        process = Popen(command)
        process.wait()
        if process.returncode != 0:
            raise ValueError(f"command returned a non-zero exit code: {process.returncode}")

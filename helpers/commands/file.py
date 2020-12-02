from shutil import copy
from typing import TYPE_CHECKING

from helpers.commands.abstract_command import AbstractCommand

if TYPE_CHECKING:
    from helpers.runner import Runner


class File(AbstractCommand):
    name = 'file'
    description = 'copies a file'

    def setup_parser(self, parser):
        """
        Setup the parser
        """
        parser.add_argument('file')

    def __call__(self, runner: 'Runner', file: str, **kwargs):
        """
        Call the command
        :param runner: The runner
        :param file: The path to the file
        """
        file = runner.get_directory() / file
        copy(file, ".")

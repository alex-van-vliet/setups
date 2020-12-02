from typing import List, TYPE_CHECKING

from helpers.commands.abstract_command import AbstractCommand

if TYPE_CHECKING:
    from helpers.runner import Runner


class Echo(AbstractCommand):
    name = 'echo'
    description = 'print arguments'

    def setup_parser(self, parser):
        """
        Setup the parser
        """
        parser.add_argument('arguments', nargs='+')

    def __call__(self, runner: 'Runner', arguments: List[str], **kwargs):
        """
        Call the command
        :param runner: The runner
        :param arguments: The values to print
        """
        print(' '.join(arguments))

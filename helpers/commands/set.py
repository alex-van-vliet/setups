from typing import TYPE_CHECKING

from helpers.argparse import check_to_type
from helpers.commands.abstract_command import AbstractCommand
from helpers.parser import is_variable

if TYPE_CHECKING:
    from helpers.runner import Runner


class Set(AbstractCommand):
    name = 'set'
    description = 'set a variable'

    def setup_parser(self, parser):
        """
        Setup the parser
        """
        parser.add_argument('variable', type=check_to_type(is_variable, "invalid name for variable"))
        parser.add_argument('value')

    def __call__(self, runner: 'Runner', variable: str, value: str, **kwargs):
        """
        Call the command
        :param runner: The runner
        :param variable: The name of the variable
        :param value: The value of the variable
        """
        runner.set_variable(variable, value)

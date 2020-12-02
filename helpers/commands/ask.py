from typing import TYPE_CHECKING, Optional

from helpers.argparse import check_to_type
from helpers.commands.abstract_command import AbstractCommand
from helpers.parser import is_variable

if TYPE_CHECKING:
    from helpers.runner import Runner


class Ask(AbstractCommand):
    name = 'ask'
    description = 'get input from the user'

    def setup_parser(self, parser):
        """
        Setup the parser
        """
        parser.add_argument('variable', type=check_to_type(is_variable, "invalid name for variable"))
        parser.add_argument('query')
        parser.add_argument('--default', default=None)

    def input(self, query: str, default: Optional[str]):
        """
        Get the input from the user
        :param query: The query string
        :param default: The default value
        :return: The input from the user
        """
        try:
            if default:
                value = input(f"{query} [{default}] ")
                if value:
                    return value
                return default
            else:
                return input(f"{query} ")
        except EOFError:
            if default:
                return default
            raise ValueError("could not read value")

    def __call__(self, runner: 'Runner', variable: str, query: str, default: Optional[str], **kwargs):
        """
        Call the command
        :param runner: The runner
        :param variable: The name of the variable
        :param query: The query string
        :param default: The default value
        """
        value = self.input(query, default)
        runner.set_variable(variable, value)

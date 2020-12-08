import re
from typing import TYPE_CHECKING, Optional

from helpers.argparse import check_to_type
from helpers.commands.abstract_command import AbstractCommand

if TYPE_CHECKING:
    from helpers.runner import Runner


def is_variable(name: str):
    REGEX = re.compile(r'^([a-zA-Z0-9_])*$')
    return REGEX.match(name)


class Ask(AbstractCommand):
    name = 'ask'
    description = 'get input from the user'

    def setup_parser(self, parser):
        """
        Setup the parser
        """
        parser.add_argument('variable', type=check_to_type(is_variable, "invalid name for variable"))
        parser.add_argument('query')
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--default', default=None)
        group.add_argument('--required', default=False, action='store_const', const=True)

    def input(self, query: str, default: Optional[str], required: bool):
        """
        Get the input from the user
        :param query: The query string
        :param default: The default value
        :param required: Whether the input is required
        :return: The input from the user
        """
        try:
            if default:
                value = input(f"{query} [{default}] ")
                if value:
                    return value
                return default
            else:
                value = input(f"{query} ")
                if required and not value:
                    raise ValueError("a value is required")
                return value
        except EOFError:
            print()
            if default:
                return default
            if required:
                raise ValueError("a value is required")
            raise ValueError("could not read value")

    def __call__(self, runner: 'Runner', variable: str, query: str, default: Optional[str], required: bool, **kwargs):
        """
        Call the command
        :param runner: The runner
        :param variable: The name of the variable
        :param query: The query string
        :param default: The default value
        :param required: Whether the input is required
        """
        value = self.input(query, default, required)
        runner.set_variable(variable, value)

import sys

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

    def __call__(self, setup, **kwargs):
        """
        Run the run command
        :param setup: The name of the setup
        :param kwargs: The arguments
        :return: Zero if there was no error, one otherwise
        """
        try:
            setup_fun(setup)
        except ValueError as e:
            print(str(e), file=sys.stderr)
            return 1

        return 0

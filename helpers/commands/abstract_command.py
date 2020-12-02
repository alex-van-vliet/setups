from argparse import ArgumentParser
from typing import Optional, Mapping, List, TYPE_CHECKING

if TYPE_CHECKING:
    from helpers.runner import Runner


class CommandArgumentParser(ArgumentParser):
    def __init__(self, prog: str, *args, **kwargs):
        """
        Creates a new command argument parser
        :param prog: The name of the command
        :param args: Arguments
        :param kwargs: Keyword arguments
        """
        super(CommandArgumentParser, self).__init__(prog=prog, add_help=False, *args, **kwargs)

    def error(self, message):
        """
        Prevents exiting and priting the message
        :param message: The error message
        """
        raise ValueError(f"invalid arguments for {self.prog}")


class AbstractCommand:
    name: str
    description: str
    parser: Optional[CommandArgumentParser]

    def __init__(self):
        """
        Create a new command
        """
        self.parser = None

    def get_name(self):
        """
        Get the name of the command
        :return: The name of the command
        """
        if not self.name:
            raise NotImplementedError("missing name value for command")
        return self.name

    def get_description(self):
        """
        Get the description of the command
        :return: The description of the command
        """
        if not self.description:
            raise NotImplementedError("missing description value for command")
        return self.description

    def init_parser(self):
        """
        Init the command parser
        """
        self.parser = CommandArgumentParser(self.get_name(), description=self.get_description())

    def setup_parser(self, parser: CommandArgumentParser):
        """
        Setup the command parser
        :param parser: The command parser
        """
        pass

    def parse(self, arguments: List[str]) -> Mapping[str, str]:
        """
        Parse the arguments
        :param arguments: The arguments to parsed
        :return: The arguments parsed
        """
        self.init_parser()
        self.setup_parser(self.parser)
        return self.parser.parse_args(arguments).__dict__

    def __call__(self, runner: 'Runner', **kwargs):
        """
        Run the command
        :param runner: The runner
        :param kwargs: The arguments
        """
        raise NotImplementedError("missing call for command")

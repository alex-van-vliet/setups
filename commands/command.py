class Command:
    name: str
    help: str

    def __init__(self):
        pass

    def get_name(self):
        """
        Get the name of the command
        :return: The name of the command
        """
        if not self.name:
            raise NotImplementedError("Missing name value for command.")
        return self.name

    def get_help(self):
        """
        Get the help of the command
        :return: The help of the command
        """
        if not self.help:
            raise NotImplementedError("Missing help value for command.")
        return self.help

    def setup_parser(self, parser):
        """
        Setup the command parser
        :param parser: The parser
        """
        pass

    def __call__(self, **kwargs):
        """
        Run the command
        :param kwargs: The arguments
        """
        raise NotImplementedError("Missing call for command.")

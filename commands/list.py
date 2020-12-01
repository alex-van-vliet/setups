from commands.command import Command
from helpers.setups import list_setups


class ListCommand(Command):
    name = "list"
    help = "list the setups"

    def __call__(self, **kwargs):
        """
        Run the list command
        :param kwargs: The arguments
        :return: Always zero
        """
        print('Available setups:')
        for setup in list_setups():
            print(setup)
        return 0

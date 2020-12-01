from pathlib import Path

from helpers.commands import run

# The directory containing the setups
DIRECTORY = Path.home() / '.setups'
# The name of a configuration file
CONFIG = '.config.setup'


def list_setups():
    """
    Yield each available setup
    """
    for subdirectory in DIRECTORY.iterdir():
        if subdirectory.is_dir():
            yield subdirectory.name


def get_setup(name):
    """
    Get the path to a setup
    :param name: The name of the setup
    :return: The path to the setup
    """
    subdirectory = DIRECTORY / name
    if not subdirectory.is_dir():
        raise ValueError(f"setup {name} does not exist")
    return subdirectory


def read_configuration(name, subdirectory):
    """
    Reads a configuration and removes comments, yields each command line
    :param name: The name of the setup
    :param subdirectory: The path to the setup
    """
    config = subdirectory / '.config.setup'
    try:
        with config.open() as f:
            for line in f.readlines():
                if line[0] != '#':
                    yield line.rstrip()
    except FileNotFoundError:
        raise ValueError(f"setup {name} does not contain a configuration file")


def setup(name):
    """
    Setup a setup
    :param name: The name of the setup
    """
    subdirectory = get_setup(name)

    for command in read_configuration(name, subdirectory):
        run(subdirectory, command)

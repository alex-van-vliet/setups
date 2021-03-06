from pathlib import Path
from shutil import copyfile
from typing import TYPE_CHECKING, Optional
from os import listdir

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
        parser.add_argument('--destination', default=None)

    def __call__(self, runner: 'Runner', file: str, destination: Optional[str], **kwargs):
        """
        Call the command
        :param runner: The runner
        :param file: The path to the file
        :param destination: Where to copy the file, based on its name if not present
        """

        def copy(file: Path, destination: Path):
            if destination.exists():
                raise ValueError(f"{destination} already exists")
            if file.is_dir():
                destination.mkdir()
                for sub in listdir(file):
                    copy(file / sub, destination / sub)
            else:
                copyfile(file, destination)

        destination = destination if destination else file
        file = runner.get_directory() / file
        destination = Path.cwd() / destination
        copy(file, destination)

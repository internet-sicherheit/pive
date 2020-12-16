from abc import ABC, abstractmethod
from pathlib import Path
from sys import stderr

class AbstractOutputManager(ABC):

    @abstractmethod
    def output(self, data, **options):
        raise NotImplemented()


class SimpleFolderOutputManager(AbstractOutputManager):

    def __init__(self, output_path):
        self.output_path = Path(output_path).resolve()

    def get_output_folder_path(self, key, options):
        return self.output_path


    def output(self, data, **options):
        for key in data:
            self.output_path.mkdir(exist_ok=True)
            if 'filenames' in options:
                filename = options['filenames'].get(key, key)
                if filename is None:
                    # Explicitly skip this file
                    continue
            else:
                filename = key
            #TODO: Process options for writing here
            with self.get_output_folder_path(key, options).joinpath(filename).open(mode="w") as outfile:
                outfile.write(data[key])

class FolderOutputManager(SimpleFolderOutputManager):
    """Similar to SimpleFolderOutputManager, but makes it possible to change the folder on a per-file basis"""

    def get_output_folder_path(self, key, options):
        if 'folders' not in options:
            #Use default output path, works the same as SimpleFolderOutputManager
            return self.output_path
        else:
            return Path(options['folders'].get(key, self.output_path))


class NullOutputManager(AbstractOutputManager):

    def __init__(self, **kwargs):
        self.verbose = kwargs.get('verbose', False)

    def output(self, data, **options):
        #Check if arguments are strings and dump them
        for key in data:
            if type(data[key]) != str:
                print(f"WARNING: Error for {key}; expected str but found {type(data[key])}", file=stderr)
            elif self.verbose:
                print(f"VERBOSE: {key}: {data[key]}", file=stderr)


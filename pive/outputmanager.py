from abc import ABC, abstractmethod
from pathlib import Path
from sys import stderr

class AbstractOutputManager(ABC):

    @abstractmethod
    def output(self, data, **options):
        raise NotImplemented()


class FolderOutputManager(AbstractOutputManager):

    def __init__(self, output_path):
        self.output_path = Path(output_path).resolve()

    def output(self, data, **options):
        for key in data:
            self.output_path.mkdir(exist_ok=True)
            if 'filenames' in options:
                filename = options['filenames'].get(key, key)
            else:
                filename = key
            #TODO: Process options for writing here
            with self.output_path.joinpath(filename).open(mode="w") as outfile:
                outfile.write(data[key])

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


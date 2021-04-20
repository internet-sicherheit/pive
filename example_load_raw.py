#!/usr/bin/env python
import pive.environment as environment
import pive.inputmanager as inputmanager
import pive.outputmanager as outputmanager
from os import listdir
from pathlib import Path
from json import load

from collections import OrderedDict

manager = inputmanager.InputManager(mergedata=False)
env = environment.Environment(inputmanager=manager, outputmanager=outputmanager.FolderOutputManager(output_path='output_reloaded'))
basepath = Path('output')
files = listdir('output')
charts = [filename[:-3] for filename in files if filename.endswith('.js')]
for chart in charts:
    with basepath.joinpath(f"{chart}_persisted.json").open("r") as persistence_file:
        chart_object = env.load_raw(persisted_data=load(persistence_file))
        chart_object.set_dataset_url(f"./{chart}.json")
        env.render(chart_object)
        code = env.render_code(chart_object)


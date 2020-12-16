#!/usr/bin/env python
import pive.environment as environment
import pive.inputmanager as inputmanager
manager = inputmanager.InputManager(mergedata=False)
env = environment.Environment(inputmanager=manager)

def get_file_mapping(chart_name):
    return {'filenames': {
        'config.json': f'{chart_name}_config.json',
        'site.html': f'{chart_name}.html',
        'chart.js': f'{chart_name}.js',
        'data.json': f'{chart_name}.json',
        'persisted.json': f'{chart_name}_persisted.json',
        'shape.json': f'{chart_name}_shape.json'
    }}

input_path = 'samples/data/metadata/numerical.json'
supported = env.load(input_path)
for x in supported:
    chart = env.choose(x)
    chart.set_width(900)
    chart.set_height(500)
    chart.set_dataset_url(f"./{x}.json")
    env.render(chart, **get_file_mapping(x))
    code = env.render_code(chart)

input_path = 'samples/data/metadata/groupdata.json'
supported = env.load(input_path)
for x in supported:
    chart = env.choose(x)
    chart.set_width(900)
    chart.set_height(500)
    chart.set_dataset_url(f"./{x}.json")
    env.render(chart, **get_file_mapping(x))
    code = env.render_code(chart)

input_path = 'samples/data/metadata/simple_series.json'
supported = env.load(input_path)
for x in supported:
    chart = env.choose(x)
    chart.set_width(900)
    chart.set_height(500)
    chart.set_dataset_url(f"./{x}.json")
    env.render(chart, **get_file_mapping(x))
    code = env.render_code(chart)

input_path = 'samples/data/hiveplot_random.json'
supported = env.load(input_path)
for x in supported:
    chart = env.choose(x)
    chart.set_width(900)
    chart.set_height(500)
    chart.set_dataset_url(f"./{x}.json")
    env.render(chart, **get_file_mapping(x))
    code = env.render_code(chart)

input_path = './samples/data/geodata/polygon.json'
manager = inputmanager.InputManager(mergedata=False)
env = environment.Environment(inputmanager=manager)
supported = env.load(input_path)
for x in supported:
    chart = env.choose(x)
    chart.set_width(900)
    chart.set_height(500)
    chart.set_dataset_url(f"./{x}.json")
    env.render(chart, **get_file_mapping(x))
    code = env.render_code(chart)

input_path = './samples/data/geodata/ge_arbeitsmarkt.csv'
manager = inputmanager.InputManager(mergedata=False)
env = environment.Environment(inputmanager=manager)
supported = env.load(input_path)
for x in supported:
    chart = env.choose(x)
    chart.set_width(900)
    chart.set_height(500)
    chart.set_dataset_url(f"./{x}.json")
    env.render(chart, **get_file_mapping(x))
    code = env.render_code(chart)

input_path = './samples/data/geodata/ge_poi-einzelhandel_small.csv'
manager = inputmanager.InputManager(mergedata=False)
env = environment.Environment(inputmanager=manager)
supported = env.load(input_path)
for x in supported:
    chart = env.choose(x)
    chart.set_width(900)
    chart.set_height(500)
    chart.set_dataset_url(f"./{x}.json")
    env.render(chart, **get_file_mapping(x))
    code = env.render_code(chart)
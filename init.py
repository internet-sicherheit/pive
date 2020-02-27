#!/usr/bin/env python
import pive.environment as environment
import pive.inputmanager as inputmanager

# Assuming you have a testdata.json file with some datapoints
# in the same directory. Try to create JSON-Objekts as Key/Value
# pairs or use a JSON formatted String Object. CSV is also
# supported.
input_path = 'samples/data/numerical.json'

###########################
### Basic usage of pive ###
###########################
# 1)Set up the environment by creating the input manager and
# passing it to an environment. Optionally, you can omit
# an output path. Default is 'output/'.
manager = inputmanager.InputManager(mergedata=False)
env = environment.Environment_(input_path, inputmanager=manager)

# 2) Load your dataset into the environment to get a
# list of supported visualizations.
supported = env.load(input_path)

# 3) Check if your desired chart is in the list and choose
# it as your visualization object. Alternatively you can
# print out the list of the supported charts and choose directly
# from it. The accessors, e.g. CHART_LINE, are environment
# constants and represent the charts included in pive.
if environment.CHART_BUBBLE in supported:
    chart = env.choose(environment.CHART_BUBBLE)

    #You can now edit the charts properties.
    chart.set_width(600)
    chart.set_height(400)

    # 4.1) Let the environment render the chart.
    # The visualizuation files will be generated
    # in the output path defined in the environment.
    env.render(chart)

    # 4.2) Optionally you can receive the
    # javascript code and its dataset as json.
    code = env.render_code(chart)
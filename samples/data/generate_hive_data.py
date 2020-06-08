import random
import json
from collections import OrderedDict

data =  []

datapoints = 10;

for item in range(datapoints):
    datapoint = OrderedDict()
    datapoint['ID'] = item
    datapoint['TYPE'] = random.choice(['A', 'B', 'C'])
    datapoint['WEIGHT'] = round(random.random(), 2)

    links = []
    number_of_links = random.randint(0,4)

    for i in range(number_of_links):
        link = random.randint(0, datapoints - 1)
        if link not in links:
            links.append(link)

    datapoint['LINKS'] = links
    data.append(datapoint)

outp = open('hiveplot_random.json', 'w')
json.dump(data, outp, indent=2)
outp.close()

# hiveplot_random_v1.json, is the one 

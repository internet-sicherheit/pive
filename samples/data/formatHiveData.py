import json

def findNode(linkID, data):
    """ Finds a node by ID to get access to its WEIGHT.
    Returns a hive conform format. """
    n = {}
    for i in data:
        if i['ID'] == linkID:
            n = {'ID':i['ID'], 'TYPE':i['TYPE'], 'WEIGHT':i['WEIGHT']}
    return n

def createLinks(data):
    """ One Datapoints has often diverse LINKS. 
    Returns a hive confom format for source and target links by ID. """
    l = []
    for i in data:
        lA = i["LINKS"]
        for j in lA:
            lID = j
            trg = findNode(lID, data)
            src = findNode(i["ID"], data)
            l.append({'source':src, 'target':trg}) # maybe errorsource
    return l

def getTypes(data):
    """ checks how many different types in the dataset are available.
    Returns a list with unique types (no duplicates). """ 
    s = {}
    for i in data:
        s.add(i["TYPE"]) # set or dict for unique counts of types.
    return s

def getNumberForType(type):
    """ Return the index of the type because hive can only handle numbers as type. """
    t = ['A', 'B', 'C', 'D', 'E']
    return t.index(type) + 1

with open("hiveplot_random.json", encoding='utf-8-sig') as json_file:
    json_data = json.load(json_file)
    links = createLinks(json_data)
    print(links)

    outp = open('hiveplot_random_format.json', 'w')
    json.dump(links, outp, indent=2)
    outp.close()

# todo: need to split node and links, too! see jinja!
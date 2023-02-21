import json


def json_path2dict(path):
    with open(path) as g:
        return json.load(g)

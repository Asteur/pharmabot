import os, json
from utils import get_entities
from collections import OrderedDict


def list2dict(l):
    _dict = {}
    for key in l:
        _dict[key] = [key]
    return _dict


def get_dict(original_dict):
    new_dict = OrderedDict()
    for key, values in original_dict.items():
        new_dict[key] = list2dict(values)
    return new_dict


def dict2json(d, out_file):
    with open(out_file, 'w') as fp:
        json.dump(d, fp)


entity_dict = get_entities('entities.txt')
dd = get_dict(entity_dict)
file_name = 'deepPavlov/DeepPavlov/download/slots/pharma.json'
output_file = os.path.join(os.path.join(os.getcwd(), os.pardir), file_name)
dict2json(dd, output_file)

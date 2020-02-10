import h5py
import numpy as np

from argparse import ArgumentParser


def get_acf(name, obj):
    if 'acf' in name:
        return name, obj

def get_ccf(name, obj):
    if 'ccf' in name:
        return name, obj

def get_group(name):
    pass

def cmp_groups():
    pass

def cmp_textFiles(src, cmp):
    pass

def cmp_cf(src, cmp):
    pass






parser = ArgumentParser()
parser.add_argument('--file', type=str, nargs=1)

args = parser.parse_args()


with h5py.File(args.file) as fd:

# Для каждого уровня содержимое следующего должно совпадать с анологичными на ом же уровне
# for layer in layers:


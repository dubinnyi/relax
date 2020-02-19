#!/usr/bin/python3 -u
### Extraction
#
import h5py

import numpy as np

from hdf5_API import hdfAPI
from argparse import ArgumentParser


def reform(file, output, tcf = '', gname = '', mean=False):
    out = h5py.File(output, 'w')

    if not hasattr(file, 'read'):
        file = hdfAPI(file, 'r')

    for group in file.get_groupList():
        pass

def main():
    parser = ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument('-o', '--output', required=False, type=str, default='out')
    parser.add_argument('--tcf', required=True, type=str)
    parser.add_argument('-g', '--gname', required=False, nargs='*', default='')
    parser.add_argument('-m', '--mean', required=False, action="store_true")
    args = parser.parse_args()
    ex_TcfNpy(args.filename, args.output, args.tcf, args.gname, args.mean)

if __name__ == '__main__':
    main()
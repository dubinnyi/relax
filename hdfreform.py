#!/usr/bin/python3 -u
import h5py

import numpy as np

from hdf5_API import hdfAPI
from argparse import ArgumentParser


def reform(args):
    file = args.filename
    output = args.output
    tcf = args.tcf
    gname = args.gname
    prefix = args.prefix if hasattr(args, 'prefix') else file

    ownfile = False
    out = h5py.File(output, 'w')

    if not hasattr(file, 'read'):
        ownfile = True
        file = hdfAPI(file, 'r')

    tcfs = tcf if tcf else file.get_tcfList()
    groups = gname if gname else file.get_groupList()

    timeline = file.get_time()
    pref = out.create_group(prefix)
    
    pref.create_dataset('time', data=timeline)
    pref.attrs['type'] = "reform"

    print("Start reform of relaxation groups from file \'{}\' to file \'{}\'".format(file, output))
    for gname in groups:
        group = pref.create_group(gname)
        group.attrs['type'] = "relaxation group"

        for tcf in tcfs:
            if not file.has_group(tcf, gname):
                continue
            print("Reforming {}".format(tcf.name))
            gtcf = group.create_group(tcf)
            gtcf.attrs['type'] = 'tcf'
            gtcf.attrs['group_size'] = file.get_groupSize(tcf, gname)
            gtcf.attrs['names'] = file.get_names(tcf, gname)

            mean, std = file.mean_tcf(tcf, gname)
            gtcf.create_dataset("group_size", data=file.get_groupSize(tcf, gname))
            gtcf.create_dataset("names", data=file.get_names(tcf, gname))
            gtcf.create_dataset("atoms", data=file.get_atoms(tcf, gname))
            gtcf.create_dataset("smarts", data=file.get_smarts(tcf, gname))
            gtcf.create_dataset("mean", data=mean)
            gtcf.create_dataset("errs", data=std)

    if ownfile:
        file.close()
    out.close()
    print("Reform of relaxation groups finished")


def main():
    parser = ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument('-o', '--output', required=False, type=str, default='out')
    parser.add_argument('--prefix', required=False, type=str)
    parser.add_argument('--tcf', required=False, nargs='*', default='')
    parser.add_argument('-g', '--gname', required=False, nargs='*', default='')
    args = parser.parse_args()
    reform(args)

if __name__ == '__main__':
    main()

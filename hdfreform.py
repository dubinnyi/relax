#!/usr/bin/python3 -u
import h5py

import numpy as np

from hdf5_API import hdfAPI
from argparse import ArgumentParser


def reform(file, output, tcf='', gname='', time_cut=None):
    ownfile = False
    out = h5py.File(output, 'w')

    if not hasattr(file, 'read'):
        ownfile = True
        file = hdfAPI(file, 'r')

    tcfs = tcf if tcf else file.get_tcfList()
    groups = gname if gname else file.get_groupList()

    step = file.get_timestep()
    space_to_del = int(time_cut // step)
    idx_del = np.arange(1, space_to_del + 1)

    timeline = file.get_time()
    timeline = np.delete(timeline, idx_del)
    out.create_dataset('time', data=timeline)

    for gname in groups:
        group = out.create_group(gname)

        for tcf in tcfs:
            if not file.has_group(tcf, gname):
                continue
            gtcf = group.create_group(tcf)
            gtcf.attrs['group_size'] = file.get_groupSize(tcf, gname)
            gtcf.attrs['names'] = file.get_names(tcf, gname)

            mean, std = file.mean_tcf(tcf, gname)
            mean = np.delete(mean, idx_del, axis=1)
            std = np.delete(std, idx_del, axis=1)
            gtcf.create_dataset("mean", data=mean)
            gtcf.create_dataset("errs", data=std)

    if ownfile:
        file.close()
    out.close()


def main():
    parser = ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument('-o', '--output', required=False, type=str, default='out')
    parser.add_argument('--tcf', required=False, nargs='*', default='')
    parser.add_argument('-g', '--gname', required=False, nargs='*', default='')
    parser.add_argument('-с', '--time-cut', required=False, default=0, type=float,\
                         help='time in ps which need to be cut from timeline')
    args = parser.parse_args()
    reform(args.filename, args.output, args.tcf, args.gname, args.time_cut)

if __name__ == '__main__':
    main()

#!/usr/bin/python3 -u
### Extraction
#
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

    timeline = file.get_time()
    if time_cut:
        # step = file.get_timestep()
        # space_to_del = time_cut // step
        # timeline = np.delete(timeline, timeline[1:space_to_del])
        timeline = np.delete(timeline, timeline[1:8])

    out.create_dataset('time', data=timeline)
    for name in groups:
        group = out.create_group(name)

        for tcf in tcfs:
            if not file._get_zeroGroup(tcf, name):
                continue
            gtcf = group.create_group(tcf)
            gtcf.attrs['group_size'] = file._get_zeroGroup(tcf, name)['group_size'][()]
            gtcf.attrs['names'] = file.get_names(tcf, name)

            mean, std = file.mean_tcf(tcf, name)
            if time_cut:
	            # step = file.get_timestep()
	            # space_to_del = time_cut // step
	            # mean = np.delete(mean, mean[1:space_to_del], axis=1)
	            mean = np.delete(mean, mean[1:8], axis=1)
	            # std = np.delete(std, std[1:space_to_del], axis=1)
	            std = np.delete(std, std[1:8], axis=1)
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
    parser.add_argument('-t', '--time-cut', required=False, default=None, type=float, help='time in ps which need to be cut from timeline')
    args = parser.parse_args()
    reform(args.filename, args.output, args.tcf, args.gname, args.time_cut)

if __name__ == '__main__':
    main()
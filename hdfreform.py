#!/usr/bin/python3 -u

import time
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import h5py
warnings.resetwarnings()

import numpy as np

from os.path import splitext, basename

from hdf5_API import hdfAPI, get_filenamePath
from argparse import ArgumentParser


def reform(args):
    filename, path = get_filenamePath(args.filename)
    output, out_path = get_filenamePath(args.output)
    tcf = args.tcf
    gname = args.gname
    prefix = args.prefix if args.prefix  else splitext(basename(filename))[0]

    ownfile = False
    out = h5py.File(output, 'w')

    if not hasattr(filename, 'read'):
        ownfile = True
        file = hdfAPI(args.filename, 'r')

    tcfs = tcf if tcf else file.get_tcfList()
    groups = gname if gname else file.get_groupList()
    max_group = max([len(g) for g in groups])

    timeline = file.get_time()
    pref = out.create_group(prefix)


    pref.attrs['type'] = "reform"

    print("Start reform of relaxation groups from file \'{}\' to file \'{}\' with prefix \'{}\'".
          format(file.filename, output, prefix))
    time_start = time.monotonic()
    time_tcf = time_start
    total_tcf = 0
    for gname in groups:
        group = pref.create_group(gname)
        group.attrs['type'] = "relaxation group"

        for tcf in tcfs:
            if not file.has_group(tcf, gname):
                continue
            g_shape = file.get_tcf_shape(tcf, gname)
            total_tcf += g_shape[0]
            folder = "\'{}/{}/{}\'".format(prefix, gname, tcf)
            shape_str = '{}'.format(g_shape)
            print("Reforming {:<40} shape = {:>14}".format(folder, shape_str), flush = True)
            gtcf = group.create_group(tcf)
            gtcf.attrs['type'] = 'tcf'
            gtcf.attrs['group_size'] = file.get_groupSize(tcf, gname)
            gtcf.attrs['names'] = file.get_names(tcf, gname)

            if args.mean and not args.logsample:
                mean, std = file.mean_tcf(tcf, gname)
            elif args.mean:
                log_arr, timeline = file.logsampling(tcf, gname)
                mean, std = file.mean_arr(log_arr)

                if args.store_all:
                    gtcf.create_dataset("logsample_traj", data=log_arr)
            else:
                print('ERROR!! Nothing to do. Should be properties mean or/and logsamle')
                return

            gtcf.create_dataset("group_size", data=file.get_groupSize(tcf, gname))
            gtcf.create_dataset("names", data=file.get_names(tcf, gname))
            gtcf.create_dataset("atoms", data=file.get_atoms(tcf, gname))
            gtcf.create_dataset("smarts", data=file.get_smarts(tcf, gname))
            gtcf.create_dataset("mean", data=mean)
            gtcf.create_dataset("errs", data=std)
            time_curr = time.monotonic()
            print(" time = {:7.2f} seconds".format(time_curr - time_tcf))
            time_tcf = time_curr

    pref.create_dataset('time', data=timeline)


    if ownfile:
        file.close()
    out.close()
    print("========= FINISHED =========")
    print("Reform of relaxation groups finished")
    print("Total number of TCFs is {}".format(total_tcf))
    print("Total time is {:7.2f} seconds".format(time_tcf - time_start))


def main():
    parser = ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument('-o', '--output', required=False, type=str, default='out')
    parser.add_argument('--prefix', required=False, type=str)
    parser.add_argument('--tcf', required=False, nargs='*', default='')
    # parser.add_argument('--logsample', type=float, default = 1.0, required=False,
                        # help='Logarithmic sampling of time points')
    parser.add_argument('-l', '--logsample', action='store_true', required=False,
                        help='Logarithmic sampling of time points')
    parser.add_argument('-a', '--store-all', required=False, action='store_true', help='Need if you want to store all trajectories in output file.')
    parser.add_argument('-g', '--gname', required=False, nargs='*', default='')
    parser.add_argument('-m', '--mean', required=False, action='store_true', help='to calculate mean of all trajectories. Will be after logsampling')
    args = parser.parse_args()
    reform(args)

if __name__ == '__main__':
    main()

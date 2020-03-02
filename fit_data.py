#!/usr/bin/python3 -u
import sys
import h5py

import numpy as np
import lmfit as lm

from fitter.fitting import Fitter
from fitter.exp_model import CModel
from argparse import ArgumentParser



def main():
    parser = ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument('-t', '--type', default='npy', help="Type of using datafile. Can be: \'npy\', \'csv\', \'hdf\'")
    parser.add_argument('-i', '--istart', default=0, type=int)
    parser.add_argument('-m', '--mode', default='NexpNtry', type=str)
    parser.add_argument('-g', '--group', help='Need to fit data from hdf')
    parser.add_argument('--tcf', default='acf', help='Need to fit data from hdf')
    args = parser.parse_args()

    if args.type == 'npy':
        fd = open(args.filename, 'rb')

        time = np.load(fd)
        data = np.load(fd)
        errs = np.load(fd)

        errs[:, 0] = errs[:, 1]

    elif args.type == 'csv':
        data = np.loadtxt(args.filename, delimiter=',')
        time = data[:, 0]
        func = data[:, 1]
        errs = np.sqrt(data[:, 2])
        # ОЧЕНЬ ВАЖНО!!
        errs[0] = errs[1]

    elif args.type == 'hdf':
        fd = h5py.File(args.filename, 'r')
        time = fd['time'][:]
        data = fd[args.group][args.tcf]['mean'][:]
        errs = fd[args.group][args.tcf]['errs'][:]

        errs[:, 0] = errs[:, 1]


    start = args.istart if args.istart < data.shape[0] else 0

    fitMod = Fitter()

    for i in range(start, data.shape[0]):
    # for i in range(1):
        if args.type == 'npy' or args.type == 'hdf':
            fitMod.fit(args.mode, data[i], errs[i], time)
        elif args.type == 'csv':
            fitMod.fit(args.mode, data, errs, time)


        if fitMod.succes:
            print(fitMod.model.res.fit_report())
            fitMod.plot_fit(i)
        else:
            print('Smth went wrong. There no fit')
            print('This happend on {} iteration'.format(i), file=sys.stderr)

        print('DONE')
    fitMod.save_toFile('out')

if __name__ == '__main__':
    main()
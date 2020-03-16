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
    parser.add_argument('-g', '--group', help='Which group you want to fit. Need to fit data from hdf')
    parser.add_argument('--tcf', default='acf', help='Need to fit data from hdf')
    parser.add_argument('-o', '--output', default='out.hdf5', help='filename with ending (npy, hdf5) for saving results')
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

    fid = h5py.File(args.output, 'w')
    grp = fid.create_group(args.group)
    exp4 = grp.create_group('exp4')
    exp5 = grp.create_group('exp5')
    exp6 = grp.create_group('exp6')
    exps = [exp4, exp5, exp6]
    for exp_grp, i in zip(exps, range(4, 7)):
        nparams = 2 * i + 1
        exp_grp.create_dataset('params', data=np.zeros((data.shape[0], nparams)))
        exp_grp.create_dataset('covar', data=np.zeros((data.shape[0], nparams, nparams)))
        exp_grp.create_dataset('stats', data=np.zeros((data.shape[0], 4)))



    for i in range(start, data.shape[0]):
        bestRes = None

        if args.type == 'npy' or args.type == 'hdf':
            bestRes = fitMod.fit(data[i], errs[i], time, method=args.mode)
        elif args.type == 'csv':
            bestRes = fitMod.fit(data, errs, time, method=args.mode)


        if fitMod.succes:
            print(fitMod.model.res.fit_report())
            fitMod.plot_fit(i)
            for group, res in zip(exps, bestRes):
                # print(res.covar)
                group['params'][i] = res.param_vals
                group['covar'][i]  = res.best_covar
                # group['stats'][i]  = res.stats


        else:
            print('Smth went wrong. There no fit')
            print('This happend on {} iteration'.format(i), file=sys.stderr)

        print('DONE')
    # fitMod.save_toFile('out')

if __name__ == '__main__':
    main()
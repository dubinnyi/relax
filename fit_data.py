#!/usr/bin/python3 -u
import sys
import h5py

import numpy as np
import lmfit as lm

from fitter.fitting import Fitter
from fitter.exp_model import CModel
from counter import Counter

from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument('-t', '--type', default='npy', help="Type of using datafile. Can be: \'npy\', \'csv\', \'hdf\'")
    parser.add_argument('-i', '--istart', default=0, type=int)
    parser.add_argument('-m', '--method', default='NexpNtry', type=str)
    parser.add_argument('-g', '--group', nargs='*', default=['NH'], help='Which group you want to fit. Need to fit data from hdf')
    parser.add_argument('--tcf', default='acf', help='Need to fit data from hdf')
    parser.add_argument('-o', '--output', default='out.hdf5', help='filename for saving results')
    args = parser.parse_args()

    counter = Counter()
    fitMod = Fitter(logger=counter.add_fitInfo)
    counter.set_curMethod(args.method)
    counter.set_curTcf(args.tcf)
    fid = h5py.File(args.output, 'w')

    for group in args.group:
        counter.set_curGroup(group)
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
            data = fd[group][args.tcf]['mean'][:]
            errs = fd[group][args.tcf]['errs'][:]

            errs[:, 0] = errs[:, 1]

            grp = fid.create_group(group)
            exps = []
            for i in fitMod.exp_iter():
                cexp = grp.create_group('exp{}'.format(i))
                exps.append(cexp)
            for exp_grp, i in zip(exps, range(4, 7)):
                nparams = 2 * i + 1
                exp_grp.create_dataset('params', data=np.zeros((data.shape[0], nparams)))
                exp_grp.create_dataset('covar', data=np.zeros((data.shape[0], nparams, nparams)))



        start = args.istart if args.istart < data.shape[0] else 0
        for i in range(start, data.shape[0]):
            counter.set_curN(i)
            bestRes = None

            if args.type == 'npy' or args.type == 'hdf':
                bestRes = fitMod.fit(data[i], errs[i], time, method=args.method)
            elif args.type == 'csv':
                bestRes = fitMod.fit(data, errs, time, method=args.method)


            try:
                print(fitMod.model.res.fit_report())
                if args.type != 'hdf':
                    continue
                for group, res in zip(exps, bestRes):
                    if res.succes:
                        group['params'][i] = res.param_vals
                        group['covar'][i]  = res.covar
                        # if res.stats:
                        #     for key, item in res.stats.items():
                        #         # save to hdf fails if item = None
                        #         if item:
                        #             group.attrs[key] = item
                    else:
                        print('Smth went wrong. There no fit', file=sys.stderr)
                        print('This happend on {} iteration {}'.format(i, '' if args.type != 'hdf' else 'in group: {}'.format(group)), file=sys.stderr)

            except Exception as e:
                print('ERROR!! Smth went wrong. There must not be any errors!', file=sys.stderr)
                print(type(e), e, file=sys.stderr)
                print('This happend on {} iteration {}'.format(i, '' if args.type != 'hdf' else 'in group: {}'.format(group)), file=sys.stderr)

            print('DONE')
    counter.save('fitStatistic.csv')
    print(counter)
    # fitMod.save_toFile('out')

if __name__ == '__main__':
    main()

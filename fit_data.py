#!/usr/bin/python3 -u
import sys
import h5py

import numpy as np
import lmfit as lm
import utils as u

from fitter.fitting import Fitter
from fitter.exp_model import CModel
from counter import Counter

from argparse import ArgumentParser

STAT_PARAMS_NAMES = ('aic', 'bic', 'chisqr', 'redchi')


def load_data(args, group):
    if args.type == 'npy':
        fd = open(args.filename, 'rb')

        time = np.load(fd)
        func = np.load(fd)
        errs = np.load(fd)

        errs[:, 0] = errs[:, 1]
        fd.close()

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
        func = fd[group][args.tcf]['mean'][:]
        errs = fd[group][args.tcf]['errs'][:]

        errs[:, 0] = errs[:, 1]
    return time, func, errs

def main():
    parser = ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument('-t', '--type', default='npy', help="Type of using datafile. Can be: \'npy\', \'csv\', \'hdf\'")
    parser.add_argument('-i', '--istart', default=0, type=int, help='index in data array for start with (DEBUG)')
    parser.add_argument('-s', '--exp-start', default=4, type=int, help='Number of exponents to start from')
    parser.add_argument('-f', '--exp-finish', default=6, type=int, help='Number of exponents when finish')
    parser.add_argument('-n', '--ntry', default=5, type=int, help='Number of tryings (for method NexpNtry)')
    parser.add_argument('-m', '--method', default='NexpNtry', type=str)
    parser.add_argument('-g', '--group', nargs='*', default=['NH'], help='Which group you want to fit. Need to fit data from hdf')
    parser.add_argument('--tcf', default='acf', help='Need to fit data from hdf')
    parser.add_argument('-o', '--output', default='out.hdf', help='filename for saving results')
    args = parser.parse_args()
    counter = Counter()
    fitMod = Fitter(logger=counter.add_fitInfo, minexp=args.exp_start, maxexp=args.exp_finish, ntry=args.ntry)
    counter.set_curMethod(args.method)
    counter.set_curTcf(args.tcf)
    fid = h5py.File(args.output, 'w')

    for group in args.group:
        counter.set_curGroup(group)
        time, data, errs = load_data(args, group)

    ## Prepare file for saving results
        grp = fid.create_group(group)
        exps = []
        for i in fitMod.exp_iter():
            cexp = grp.create_group('exp{}'.format(i))
            exps.append(cexp)
        for exp_grp, i in zip(exps, range(4, 7)):
            nparams = 2 * i + 1
            exp_grp.create_dataset('params', data=np.zeros((data.shape[0], nparams)))
            exp_grp.create_dataset('covar', data=np.zeros((data.shape[0], nparams, nparams)))
            exp_grp.create_dataset('stats', data=u.create_nameArray(data.shape[0], STAT_PARAMS_NAMES))



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
                # if args.type != 'hdf':
                #     continue
                for group_hdf, res in zip(exps, bestRes):
                    if res.success:
                        # print(res)
                        group_hdf['params'][i] = res.param_vals
                        group_hdf['covar'][i]  = res.covar
                        ## !!! ОЧЕНЬ УПОРОТЫЙ МЕТОД ИЗ-ЗА НЕВОЗМОЖНОСТИ ПОЭЛЕМЕНТНОЙ ЗАМЕНЫ ЭЛЕМЕНТОВ ДАТАСЕТА.
                        stat_list = []
                        for key in STAT_PARAMS_NAMES:
                            vals = res.stats
                            stat_list += [vals[key]]

                        group_hdf['stats'][i] = tuple(stat_list)
                        ## КОНЕЦ УПОРОТОГО МОМЕНТА
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

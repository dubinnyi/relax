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
        with open(args.filename, 'rb') as fd:

            time = np.load(fd)
            func = np.load(fd)
            errs = np.load(fd)

            errs[:, 0] = errs[:, 1]
            names = [str(i) for i in range(func.shape[0])]


    elif args.type == 'csv':
        data = np.loadtxt(args.filename, delimiter=',')
        time = data[:, 0]
        func = [ data[:, 1] ]
        errs = [ np.sqrt(data[:, 2]) ]
        names = [args.filename]
        # ОЧЕНЬ ВАЖНО!!
        errs[0] = errs[1]

    elif args.type == 'hdf':
        fd = h5py.File(args.filename, 'r')
        time = fd['time'][:]
        func = fd[group][args.tcf]['mean'][:]
        errs = fd[group][args.tcf]['errs'][:]
        names = fd[group][args.tcf].attrs['names']
        names = names.splitlines()
        errs[:, 0] = errs[:, 1]
    else:
        (time, func, errs, names) = (None, None, None, None)
    return time, func, errs, names

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
    ### ВРЕМЕННЫЕ АРГУМЕНТЫ
    parser.add_argument('-e', '--fix-errors', action="store_true")
    parser.add_argument('-c', '--count-trj', required=False, type=int)
    parser.add_argument('-w', '--time-cut', required=False, default=0, type=float, help='time in ps which need to be cut from timeline')
    ###
    args = parser.parse_args()
    counter = Counter()
    fitMod = Fitter(logger=counter.add_fitInfo, minexp=args.exp_start, maxexp=args.exp_finish, ntry=args.ntry)
    counter.set_curMethod(args.method)
    counter.set_curTcf(args.tcf)
    fid = h5py.File(args.output, 'w')

    for group in args.group:
        counter.set_curGroup(group)
        time, data, errs, names = load_data(args, group)

        ### ВРЕМЕННЫЙ УЧАСТОК
        if args.fix_errors:
            if errs:
                errs = errs / np.sqrt(args.count_trj)

        if args.time_cut != 0:
            # step = file.get_timestep()
            # space_to_del = time_cut // step
            time = np.delete(time, time[1:space_to_del])
            data = np.delete(data, data[1:space_to_del], axis=1)
            errs = np.delete(errs, errs[1:space_to_del], axis=1)
            time = np.delete(time, time[1:7])
            data = np.delete(data, data[1:7], axis=1)
            errs = np.delete(errs, errs[1:7], axis=1)
        ### КОНЕЦ ВРЕМЕННОГО УЧАСТКА
        data_size = data.shape[0]

    ## Prepare file for saving results
        grp = fid.create_group(group)
        exps = []
        for i in fitMod.exp_iter():
            cexp = grp.create_group('exp{}'.format(i))
            exps.append(cexp)
        for exp_grp, i in zip(exps, range(args.exp_start, args.exp_finish + 1)):
            nparams = 2 * i + 1
            exp_grp.create_dataset('params', data=np.zeros((data_size, nparams)))
            exp_grp.create_dataset('covar', data=np.zeros((data_size, nparams, nparams)))
            exp_grp.create_dataset('stats', data=u.create_nameArray(data_size, STAT_PARAMS_NAMES))



        start = args.istart if args.istart < data_size else 0
        for i in range(start, data_size):
            # set name, not index
            counter.set_curN(names[i])
            name_string = "{:10} {:25}".format(group, names[i])
            bestRes = fitMod.fit(data[i], errs[i], time, method=args.method, name_string = name_string)

            try:
                if not fitMod.anyResult:
                    pass
                else:
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
                            print("{}: fit failed".format(name_string), file=sys.stderr)
                            #print('This happend on {} iteration {}'.format(i, '' if args.type != 'hdf' else 'in group: {}'.format(group)), file=sys.stderr)


            except Exception as e:
                print("{}: ERROR in fit".format(name_string), file=sys.stderr)
                print(type(e), e, file=sys.stderr)
                #print('This happend on {} iteration {}'.format(i, '' if args.type != 'hdf' else 'in group: {}'.format(group)), file=sys.stderr)

            print("{}: DONE".format(name_string))
    counter.save('fitStatistic.csv')
    print(counter)
    # fitMod.save_toFile('out')

if __name__ == '__main__':
    main()

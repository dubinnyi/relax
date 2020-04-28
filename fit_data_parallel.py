#!/usr/bin/python3 -u
import sys
import h5py
import copy
from threadpoolctl import threadpool_limits

import numpy as np
import lmfit as lm
import utils as u

from fitter.fitting import Fitter
from fitter.exp_model import CModel
from counter import Counter

from argparse import ArgumentParser
from multiprocessing import Pool, cpu_count

STAT_PARAMS_NAMES = ('aic', 'bic', 'chisqr', 'redchi')
NCPU = cpu_count()

#os.system("taskset -p 0xff %d" % os.getpid())

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
        with h5py.File(args.filename, 'r') as fd:
            time = fd['time'][:]
            func = fd[group][args.tcf]['mean'][:]
            errs = fd[group][args.tcf]['errs'][:]
            names = fd[group][args.tcf].attrs['names']
            names = names.splitlines()
            errs[:, 0] = errs[:, 1]
    else:
        (time, func, errs, names) = (None, None, None, None)
    return time, func, errs, names

def prepare_data(time, data, errs, time_cut):
    step = time[1] - time[0]
    space_to_del = int(time_cut // step)
    idx_del = np.arange(1, space_to_del + 1)
    time = np.delete(time, idx_del)
    data = np.delete(data, idx_del, axis=1)
    errs = np.delete(errs, idx_del, axis=1)
    return time, data, errs

def pool_fit_one(args):
    group = args['group']
    data = args['data']
    counter = args['counter']
    fitMod = args['fitter']
    names = args['names']
    errs = args['errs']
    time = args['time']
    s, f = args['indexes']
    fitMod.logger = counter.add_fitInfo

    parallelResults = [None]
    for i, ci in zip(range(s, f), range(f-s)):
        counter.set_curN(names[ci])
        name_string = "{:10} {:25}".format(group, names[ci])
        bestRes = fitMod.fit(data[ci], errs[ci], time, method=args['method'], name_string = name_string)
        parallelResults[ci] = (i, bestRes)
        print("{}: DONE".format(name_string))
    return counter, parallelResults, name_string

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
    parser.add_argument('-c', '--time-cut', default=0, type=float,\
                         help='time in ps which need to be cut from timeline')
    args = parser.parse_args()
    fid = h5py.File(args.output, 'w')
    counter = Counter()

    for group in args.group:
        fitMod = Fitter(minexp=args.exp_start, maxexp=args.exp_finish, ntry=args.ntry)
        counter.set_curMethod(args.method)
        counter.set_curTcf(args.tcf)
        counter.set_curGroup(group)
        time, data, errs, names = load_data(args, group)
        time, data, errs = prepare_data(time, data, errs, args.time_cut)
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

        # prepare arguments for parallel fitting
        csize = data_size - start

        nproc = min(csize, NCPU)
        step = csize // nproc
        arg_list = [{'data': data[s:s+step], 'errs': errs[s:s+step], 'time': time, 'indexes': (s, s+step), 'names': names[s:s+step], 'group': group, 'fitter': copy.copy(fitMod), 'method':args.method, 'counter': copy.copy(counter)} for s in range(start, data_size, step)]
        # print(arg_list)
        print("Start pool of {} CPU".format(nproc))
        with threadpool_limits(limits=1, user_api='blas'):
            pool = Pool(processes=nproc)
            res_par = pool.map_async(pool_fit_one, arg_list)

            pool.close()
            pool.join()
            res_par.wait()
            result = res_par.get()

            try:
                for rc, rf, name_string in result:
                    counter = counter + rc
                    for (i, bestRes) in rf:
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

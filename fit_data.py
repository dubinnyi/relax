#!/usr/bin/python3 -u
import sys

import numpy as np
import lmfit as lm

from classes.fitting import Fitting
from classes.exp_model import CModel
from argparse import ArgumentParser



def main():
    parser = ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument('-t', '--type', default='npy')
    args = parser.parse_args()

    if args.type == 'npy':
        fd = open(args.filename, 'rb')

        time = np.load(fd)

        for _ in range(10):

            data = np.load(fd)
            errs = np.load(fd)

            errs[:, 0] = errs[:, 1]
            # print(errs[:, :4])

            # for i in range(data.shape[0]):
            for i in range(1):
                fitMod = Fitting(data[i], errs[i], time)
                fitMod.add_model(4)
                fitMod.fit()
                print(fitMod.model.res.fit_report())
                fitMod.plot_fit(i)
                print('DONE')
            fitMod.save_toFile('out')

    elif args.type == 'csv':
        data = np.loadtxt(args.filename, delimiter=',')
        time = data[:, 0]
        func = data[:, 1]
        errs = data[:, 2]
        # ОЧЕНЬ ВАЖНО!!
        errs[0] = errs[1]

        exp_mod = Fitting(func[:], np.sqrt(errs[:]), time[:])
        exp_mod.add_model(4)
        exp_mod.fit()
        print(exp_mod.res.fit_report())
        exp_mod.plot_fit(4)
        print('DONE')
        exp_mod.save_toFile('out')

if __name__ == '__main__':
    main()

# fname = sys.argv[1]
# facf = sys.argv[1]
# fstd = sys.argv[2]
# ftime = sys.argv[3]



# time = np.load(ftime)
# data = np.load(facf)
# errs = np.load(fstd)

# errs[:, 0] = errs[:, 1]

# for i in range(3):
#     fitMod = Fitting(data[i], errs[i], time)
#     fitMod.add_model(2)
#     fitMod.fit()
#     print(fitMod.model.res.fit_report())
#     fitMod.plot_fit(i)
#     print('DONE')statistic(args.filename, args.all)


# d = exp_mod.res.best_values

# print(exp_mod.res.covar)

# def f(x, aamplitude, bamplitude, camplitude, damplitude, c, adecay, bdecay, cdecay, ddecay, eamplitude, edecay):
#     return c + aamplitude * np.exp(-x/adecay) + bamplitude * np.exp(-x/bdecay) + camplitude * np.exp(-x/cdecay) +damplitude * np.exp(-x/ddecay) + eamplitude * np.exp(-x/edecay)
# print(f(0, **d))
# exp_mod.plot_logfit()

#!/usr/bin/python3 -u
import sys

import numpy as np
import lmfit as lm

from fitting import Fitting
from exp_model import CModel
from argparse import ArgumentParser




def main():
    parser = ArgumentParser()
    parser.add_argument("filename", type=str)
    args = parser.parse_args()

    fd = open(args.filename, 'rb')

    time = np.load(fd)

    for _ in range(10):

        data = np.load(fd)
        errs = np.load(fd)

        errs[:, 0] = errs[:, 1]
        print(errs)

        for i in range(data.shape[0]):
            fitMod = Fitting(data[i], errs[i], time)
            fitMod.add_model(2)
            fitMod.fit()
            print(fitMod.model.res.fit_report())
            fitMod.plot_fit(i)
            print('DONE')


if __name__ == '__main__':
    main()


# facf = sys.argv[1]
# fstd = sys.argv[2]
# ftime = sys.argv[3]

# # data = np.loadtxt(fname, delimiter=',')

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

# time = data[:, 0]
# func = data[:, 1]
# errs = data[:, 2]
# ОЧЕНЬ ВАЖНО!!
# errs[0] = errs[1]

# exp_mod = Fitting(func[:], np.sqrt(errs[:]), time[:])
# exp_mod.add_model(2)

# initial_values = {'aamplitude' : 0.01,
#                   'bamplitude' : 0.01,
#                   'camplitude' : 0.01,
#                   'damplitude' : 0.01,
#                   'eamplitude' : 0.01,
#                   # 'famplitude' : 0.01,
#                   'c' : 0.1,
#                   'adecay' : 1,
#                   'bdecay' : 10,
#                   'cdecay' : 50,
#                   'ddecay' : 100,
#                   'edecay' : 1000}
                  # 'fdecay' : 3000}

# initial_values = {'aamplitude' : 0.01,
#                   'c' : 0.1,
#                   'adecay' : 1}

# exp_mod.fit()
# print(exp_mod.model.res.fit_report())
# d = exp_mod.res.best_values

# print(exp_mod.res.covar)

# def f(x, aamplitude, bamplitude, camplitude, damplitude, c, adecay, bdecay, cdecay, ddecay, eamplitude, edecay):
    # return c + aamplitude * np.exp(-x/adecay) + bamplitude * np.exp(-x/bdecay) + camplitude * np.exp(-x/cdecay) +damplitude * np.exp(-x/ddecay) + eamplitude * np.exp(-x/edecay)
# print(f(0, **d))
# exp_mod.plot_logfit()
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
    parser.add_argument('-i', '--istart', default=0, type=int)
    parser.add_argument('-m', '--mode', default='NexpNtry', type=str)
    args = parser.parse_args()

    if args.type == 'npy':
        fd = open(args.filename, 'rb')

        time = np.load(fd)
        data = np.load(fd)
        errs = np.load(fd)

        errs[:, 0] = errs[:, 1]
        # print(errs[:, :4])

    elif args.type == 'csv':
        data = np.loadtxt(args.filename, delimiter=',')
        time = data[:, 0]
        func = data[:, 1]
        errs = np.sqrt(data[:, 2])
        # ОЧЕНЬ ВАЖНО!!
        errs[0] = errs[1]

    start = args.istart if args.istart < data.shape[0] else 0

    fitMod = Fitting()

    for i in range(start, data.shape[0]):
    # for i in range(1):
        if args.type == 'npy':
            fitMod.fit(args.mode, data[i], errs[i], time)
        elif args.type == 'csv':
            fitMod.fit(args.mode, data, errs, time)

        if fitMod.succes:
            print(fitMod.model.res.fit_report())
            fitMod.plot_fit(i)
        else:
            print('Smth went wrong. There no fit')
            print('This happend on {} iteration'.format(i))

        print('DONE')
    fitMod.save_toFile('out')

if __name__ == '__main__':
    main()
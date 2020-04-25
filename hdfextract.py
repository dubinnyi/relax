#!/usr/bin/python3 -u
### Extraction
#
import numpy as np

from hdf5_API import hdfAPI
from argparse import ArgumentParser


def ex_TcfNpy(file, output, tcf, gname = '', mean=False):
    ownfile = False
    if not hasattr(file, 'read'):
        file = hdfAPI(file, 'r')
        ownfile = True

    fd = open(output + '.npy', 'wb')
    fd2 = open(output + '_pairs.txt', 'a')
    t = file.get_time()
    np.save(fd, t)
    # gname = gname[0]
    if gname:
        groups = [gname] if type(gname) == str else gname
    else:
        groups = file.get_groupList(tcf=tcf)

    for group in groups:
        if mean:
            average, std = file.mean_tcf(tcf, group)
            np.save(fd, average)
            np.save(fd, std)
        # else:
        #     np.save(fd, g['cf'])
        names = file.get_names(tcf, group)
        print(names, file=fd2)
    fd.close()
    fd2.close()
    if ownfile:
        file.close()

def main():
    parser = ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument('-o', '--output', required=False, type=str, default='out')
    parser.add_argument('--tcf', required=True, type=str)
    parser.add_argument('-g', '--gname', required=False, nargs='*', default='')
    parser.add_argument('-m', '--mean', required=False, action="store_true")
    args = parser.parse_args()
    ex_TcfNpy(args.filename, args.output, args.tcf, args.gname, args.mean)

if __name__ == '__main__':
    main()
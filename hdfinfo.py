#!/usr/bin/python3 -u
#
from hdf5_API import hdfAPI
from argparse import ArgumentParser
from prettytable import PrettyTable

def statistic(file, all=False):
        ownfile = False
        if not hasattr(file, 'read'):
            file = hdfAPI(file, 'r')
            ownfile = True

        print('_________STATISTIC_________')
        print('Checking....', end='')

        if file.check_file():
            print('OK')
        else:
            print('Failed')
            return

        print('Traces......', file.get_trjCount(), sep='')

        print('Timeline....', file.get_time()[-1], 'ps', sep='')
        pt = PrettyTable()
        pt.field_names = ['Group', 'acf', 'ccf']

        allg = {}
        total = {'acf': 0, 'ccf': 0}
        groups = file.get_groupList()

        print('Groups......', len(groups), sep='')

        for gname in sorted(list(groups)):
            allg = {'acf':0, 'ccf': 0}
            for tcf in ['acf', 'ccf']:
                for group in file.group_iter(tcf, gname, all):
                    cf_len = len(group['cf'])
                    allg[tcf] += cf_len
                    total[tcf] += cf_len
            pt.add_row([gname, allg['acf'], allg['ccf']])

        pt.add_row(['TOTAL', total['acf'], total['ccf']])
        print(pt)

        if ownfile:
            file.close()

def main():
    parser = ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument('-a', '--all', required=False, action="store_true")
    args = parser.parse_args()
    statistic(args.filename, args.all)


if __name__ == '__main__':
    main()
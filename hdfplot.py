#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  hdfplot.py
#
#  Copyright 2020 Svetlana Nolde <sveta@elk.localdomain>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import h5py
import numpy as np
import matplotlib.pyplot as plt

from argparse import ArgumentParser

def expall(param,arrtime):
	nexp=(param.shape[0]-1)//2
	out=np.copy(param[-1])
	for i in range(nexp):
		out = out + param[2*i]*np.exp(arrtime/(-param[2*i+1]))
	return out


def main(args):
    parser = ArgumentParser()
    parser.add_argument("-d", '--data-file', type=str)
    parser.add_argument("-f", '--fit-file', type=str)
    parser.add_argument("-n", '--name-file', type=str)
    parser.add_argument('-g', '--group', default='NH', help='Which group you want to plot')
    parser.add_argument('--tcf', default='acf')
    # parser.add_argument('-s', '--exp-start', default=4, type=int, help='Number of exponents to start from')
    # parser.add_argument('-f', '--exp-finish', default=6, type=int, help='Number of exponents when finish')
    args = parser.parse_args()

	with h5py.File(args.data_file, 'r') as f:
		arrtime=np.array(f.get('time'))
		nh=np.array(f.get('{}/{}/mean'.format(args.group, args.tcf)))
		nherr=np.array(f.get('{}/{}/errs'.format(args.group, args.tcf)))


	with h5py.File(args.fit_file, 'r') as f:
		exp4=np.array(f.get('{}/exp4/params'.format(args.group)))
		exp5=np.array(f.get('{}/exp5/params'.format(args.group)))
		exp6=np.array(f.get('{}/exp6/params'.format(args.group)))

	with h5py.File(args.name_file, 'r') as f:
		rlist=np.array(f.get('GB1_c36m_npt_rand1_S01/{}/{}/names'..format(args.tcf, args.group)))
		resname=rlist.astype(str)[()].split('\n')
		# print(resname,len(resname),type(resname))

	for res in range(nh.shape[0]):
		fig,ax=plt.subplots(1,2, figsize=(10,5))
		fig.suptitle(resname[res].split()[4:7])
		ax[0].errorbar((arrtime+1)[:7],nh[res,:7],
			yerr=nherr[res,:7], fmt=' ',zorder=0, color='m')
		for xsel in (slice(7,3000,None),slice(3000,6000,5),
						slice(6000,None,25)):
			ax[0].errorbar((arrtime+1)[xsel],nh[res,xsel],
			yerr=nherr[res,xsel], fmt=' ',zorder=0, color='C0')
		ax[0].set_xscale('log')

		for expdata, explabel, col in zip((exp4, exp5, exp6),
			('4 exps','5 exps','6 exps'), ('C1', 'C2', 'C3')):
			if(expdata[res,-1]>0):
				ax[0].plot(arrtime+1, expall(expdata[res],arrtime),
						label=explabel, zorder=10, color=col)

		ax[0].legend()

		ntime=200
		ax[1].errorbar(arrtime[1:7]+1, nh[res,1:7],
					yerr=nherr[res,1:7], fmt=' ',zorder=0, color='m')
		ax[1].errorbar(arrtime[7:ntime]+1,nh[res,7:ntime],
					yerr=nherr[res,7:ntime],fmt=' ',zorder=0)
		ax[1].set_xscale('log')
		ylim=ax[1].get_ylim()
		for expdata, explabel, col  in zip((exp4, exp5, exp6),
			('4 exps','5 exps','6 exps'), ('C1', 'C2', 'C3')):
			if(expdata[res,-1]>0):
				ax[1].plot((arrtime[1:ntime]+1),
						 expall(expdata[res,:ntime],
						 arrtime[:ntime])[1:],
						 label=explabel, zorder=10, color=col)
		ax[1].set_ylim(ylim)
		ax[1].legend()
		plt.show()
		plt.close()

	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

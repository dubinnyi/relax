#!/usr/bin/python3 -u

import numpy as np
import multiprocessing as mproc
import lmfit
import time

from fitter.fitting import Fitter

npts=128
nruns_seq=128
nruns_par=8192*8
nruns = max(nruns_seq,nruns_par)
#ncpu=mproc.cpu_count()
ncpu=32
npars=2 # A and T in exp_one
sigma=0.01

dataX=np.linspace(npts,1,npts)

def exp_one(x, A, T):
    return A * np.exp(-T * x)

def random_AT(nruns):
    return np.random.random([nruns,npars])

def exp_one_data(at):
    exp = lambda x: exp_one(x,*at)
    dataY = np.fromiter(map(exp, dataX),dtype=float)
    dataY+= np.random.normal(0.0, sigma, npts)
    return dataY

def one_fit(tuple_of_args):
    (dataY, model, params) = tuple_of_args
    return model.fit(dataY, params, x=dataX, method='least_squares', scale_covar=False)

def random_XY(AT):
    nruns= AT.shape[0]
    rdata= np.empty([nruns, npts])
    for i, at in zip(range(nruns),AT):
        rdata[i]= exp_one_data(at)
    return rdata

if __name__ == '__main__':
    rat=random_AT(nruns)
    print(rat.shape)
    print(rat)
    rdata=random_XY(rat)
    print(rdata.shape)
    print(rdata)



    exp_model=lmfit.Model(exp_one)
    params=exp_model.make_params(A=0.5,T=0.5)
    print("Run one fit")
    start=time.monotonic()
    res = exp_model.fit(rdata[0], params, x=dataX, method='least_squares', scale_covar=False)
    print(res.fit_report())
    print(rat[0])
    finish=time.monotonic()
    print("one fit finished after {} seconts".format(finish-start))

    res=[]
    print()
    print("Run {} fits sequencially".format(nruns_seq))
    start=time.monotonic()
    for i in range(nruns_seq):
        targ=(rdata[i], exp_model, params)
        res.append(one_fit(targ))
    finish=time.monotonic()
    print("Sequencial fits finished after {} seconds, {} fits/sec".format(finish-start,(finish-start)/nruns_seq))

    chunk_size= int(nruns_par/ncpu)
    print()
    print("Run {} fits in parallel on {} CPU, chunk_size={}".format(nruns_par, ncpu, chunk_size))
    pool = mproc.Pool(ncpu)
    start=time.monotonic()
    fit_arg_list = [(rdata[i], exp_model, params) for i in range(nruns_par)]
    respar=pool.map_async(one_fit, fit_arg_list, chunk_size)

    pool.close()
    pool.join()
    respar.wait()

    par_results= respar.get()
    finish=time.monotonic()
    print(rat[0])
    print(par_results[0].best_values)
    print("Parallel fits finished after {} seconds, {} fits/sec".format(finish-start, (finish-start)/nruns_par))




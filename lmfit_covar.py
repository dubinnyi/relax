#!/usr/bin/python3 -u

import numpy as np
import multiprocessing as mp
from threadpoolctl import threadpool_limits
import lmfit
import time


def exp_one(x, A, T):
    return A * np.exp(-T * x) 

def random_AT(nruns):
    return np.random.random([nruns,npars])

def add_random_noise(dataY, sigma):
    return dataY + np.random.normal(0, sigma, dataY.shape[0])

def exp_one_data(dataX, at):
    #exp = lambda x: exp_one(x,*at)
    #dataY = np.fromiter(map(exp, dataX),dtype=float)
    dataY = exp_one(dataX, at[0], at[1])
    dataY+= np.random.normal(0.0, sigma, npts)
    return dataY

def one_fit(tuple_of_args):
   (dataX, dataY, model, params) = tuple_of_args
   return model.fit(dataY, params, x=dataX, method='least_squares', scale_covar=False)

def one_fit_with_weights(tuple_of_args):
   (dataX, dataY, model, params, weights) = tuple_of_args
   return model.fit(dataY, params, x=dataX, method='least_squares', scale_covar=False)

def random_XY(dataX, AT):
    nruns= AT.shape[0]
    rdata= np.empty([nruns, npts])
    for i, at in zip(range(nruns),AT):
      rdata[i]= exp_one_data(dataX, at)
    return rdata

def run_one_fit(dataX, rdataYi, rAT, model, params):
    print()
    print("Run one fit")
    start = time.monotonic()
    res= model.fit(rdataYi, params, x=dataX, method='least_squares', scale_covar=False)
    finish = time.monotonic()
    print("one fit finished after {} seconts, {} fits/sec".\
          format(finish - start, 1/(finish - start)))
    print(" Fit params= {}".format(str(res.best_values)))
    print("True params= {{\'A\': {}, \'T\': {} }}".format(rAT[0], rAT[1]))
    return res

def run_fits_sequencially(dataX, rdataY, rAT, model, params, nruns):
    results = []
    print()
    print("Run {} fits sequencially".format(nruns_seq))
    start = time.monotonic()
    for i in range(nruns):
        targ = (dataX, rdataY[i], model, params)
        results.append(one_fit(targ))
    finish = time.monotonic()
    print("Sequencial fits finished after {} seconds, {} fits/sec".\
          format(finish - start, nruns_seq / (finish - start) ))
    return results

def run_fits_parallel(dataX, rdataY, rAT, model, params, nruns_par):
    chunk_size = int(nruns_par / ncpu)
    print()
    print("Run {} fits in parallel on {} CPU, chunk_size={}".format(nruns_par, ncpu, chunk_size))
    fit_arg_list = [(dataX, rdataY[i], model, params) for i in range(nruns_par)]

    with threadpool_limits(limits=1, user_api='blas'):

        start = time.monotonic()
        pool = mp.Pool(ncpu)

        respar = pool.map_async(one_fit, fit_arg_list, chunk_size)
        pool_time = time.monotonic()
        print("{:>32} {:7.4f} seconds".format("pool submitted after", pool_time - start))

        pool.close()
        close_time = time.monotonic()
        print("{:>32} {:7.4f} seconds".format("pool closed after", close_time - start))

        pool.join()
        join_time = time.monotonic()
        print("{:>32} {:7.4f} seconds".format("pool joined after", join_time - start))

        respar.wait()
        wait_time = time.monotonic()
        print("{:>32} {:7.4f} seconds".format("wait for results finished after", wait_time - start))

        par_results = respar.get()
        get_time = time.monotonic()
        print("{:>32} {:7.4f} seconds".format("get of results finished after", get_time - start))

        finish = time.monotonic()

        iprint=0
        print()
        print(" Fit params[{}]= {}".format(iprint, str(par_results[iprint].best_values)))
        print("True params[{}]= {{\'A\': {}, \'T\': {} }}".format(iprint, rAT[iprint,0], rAT[iprint,1]))
        print("Parallel fits finished after {} seconds, {} fits/sec".\
              format(finish - start, nruns_par/ (finish - start)))
    return par_results


def run_monte_carlo_covar(dataX, A0, T0, sigma, ntry= 16):
    print()
    print("Run monte-carlo covariance matrix estimation")
    print("A0={}, T0={}, sigma={}, ntry={}".format(A0,T0,sigma,ntry))
    dataY= exp_one(dataX, A0, T0)
    exp_model = lmfit.Model(exp_one)
    params = exp_model.make_params(A=A0, T=T0)
    weights = np.full(dataX.shape, 1/sigma)

    noise_small= 1e-10
    print("Initial exact fit with weights = 1/sigma and noise = {}".format(noise_small))

    dataY_noise= add_random_noise(dataY, noise_small)
    all_args = (dataX, dataY_noise, exp_model, params, weights)
    fit_res= one_fit_with_weights(all_args)
    best = fit_res.best_values
    covar = fit_res.covar
    print(" Fit params: A= {:8.6f} T= {:8.6f}".format(best['A'], best['T']))
    print("True params: A= {:8.6f} T= {:8.6f}".format(A0, T0))
    print("COVAR =\n{}".format(covar))
    param_stat=np.zeros((2,ntry))

    print()
    print("Monte-Carlo covariance matrix estimation by {} fits ".format(ntry))
    for i in range(ntry):
        dataY_noise = add_random_noise(dataY, sigma)
        all_args = (dataX, dataY_noise, exp_model, params, weights)
        fit_res = one_fit_with_weights(all_args)
        best = fit_res.best_values
        param_stat[0, i] = best['A'] - A0
        param_stat[1, i] = best['T'] - T0
    print("Monte carlo finished")
    mc_covar = np.cov(param_stat)
    print("MC_COVAR=\n{}".format(mc_covar))

    print("1e6*MC_COVAR/COVAR = \n{}".format(1e6*mc_covar/covar))

    return covar, mc_covar


if __name__ == '__main__':

    npts = 128
    nruns_seq = 128
    ncpu = mp.cpu_count()
    nruns_par = 32 * ncpu
    nruns = max(nruns_seq, nruns_par)
    # ncpu=4
    npars = 2  # A and T in exp_one
    sigma = 0.01
    dataX = np.linspace(npts, 1, npts)


    print("Generate data for tests")
    print("Generate exp_model")
    exp_model = lmfit.Model(exp_one)
    print("Generate exp_params")
    exp_params = exp_model.make_params(A=0.5, T=0.5)
    print("Generate random A and T values (rAT) of size {}".format(nruns))
    rAT=random_AT(nruns)
    print("Generate random_XY of size {}".format(rAT.shape[0]))
    rdata = random_XY(dataX, rAT)
    print("Data for tests ready")

    #irun=0
    #res0 = run_one_fit(dataX, rdata[irun], rAT[irun], exp_model, exp_params)

    #resseq= run_fits_sequencially(dataX, rdata, rAT, exp_model, exp_params, nruns_seq)

    #respar= run_fits_parallel(dataX, rdata, rAT, exp_model, exp_params, nruns_par)

    res_covar1 = run_monte_carlo_covar(dataX, 0.5, 0.5, 0.01, 1024)
    res_covar2 = run_monte_carlo_covar(dataX, 0.5, 0.5, 0.02, 1024)
    res_covar3 = run_monte_carlo_covar(dataX, 0.5, 0.5, 0.03, 1024)







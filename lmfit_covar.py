#!/usr/bin/python3 -u

import numpy as np
import multiprocessing as mp
from threadpoolctl import threadpool_limits
import lmfit
import time
import argparse
import matplotlib.pyplot as plt


def exp_one(x, A, T):
    return A * np.exp(-x/T)


def exp_two_c(x, A1, T1, A2, T2, c):
    return A1 * np.exp(-x/T1) + A2 * np.exp(-x/T2) + c


def expNfree(x, A, T, c):
    ret = np.full(x.shape, c) if hasattr(x,'shape') else c
    for a,t in zip(A,T):
        ret+= a * np.exp(-t*x)
    return ret


def random_AT(nruns, npars):
    return np.random.random([nruns,npars]) + 0.25


def add_random_noise(dataY, sigma):
    return dataY + np.random.normal(0, sigma, dataY.shape[0])


def exp_one_data(dataX, at, sigma):
    npts = dataX.shape[0]
    dataY = exp_one(dataX, at[0], at[1])
    dataY+= np.random.normal(0.0, sigma, npts)
    return dataY


def one_fit(tuple_of_args):
   (dataX, dataY, model, params, weights) = tuple_of_args
   return model.fit(dataY, params, x=dataX, weights=weights, method='least_squares', scale_covar=False)


def one_fit_with_weights_scalecovar(tuple_of_args):
   (dataX, dataY, model, params, weights, scalecovar) = tuple_of_args
   return model.fit(dataY, params, x=dataX, weights=weights, method='least_squares', scale_covar=scalecovar)


def random_XY(dataX, AT, sigma):
    nruns= AT.shape[0]
    rdata= np.empty([nruns, npts])
    for i, at in zip(range(nruns),AT):
      rdata[i]= exp_one_data(dataX, at, sigma)
    return rdata


def run_one_fit(dataX, rdataY, weights, rAT, model, params):
    print()
    print("Run one fit")
    start = time.monotonic()
    res= model.fit(rdataY, params, x=dataX, weights=weights, method='least_squares', scale_covar=False)
    finish = time.monotonic()
    print("one fit finished after {} seconts, {} fits/sec".\
          format(finish - start, 1/(finish - start)))
    print(res.fit_report())
    print("Compariosion with TRUE values")
    print("{:>10} {:13} {:13}".format("Name","Fit","True"))
    ipar= 0
    for par_name, par_fit in res.best_values.items():
        print("{:>10} {:13.10f} {:13.10f}".format(par_name, par_fit, rAT[ipar]))
        ipar += 1
    print("Covariance matrix:")
    print(res.covar)

    res.plot()
    plt.show()
    plt.close()
    return res


def run_fits_sequencially(dataX, rdataY, weights, rAT, model, params, nruns):
    results = []
    print()
    print("Run {} fits sequencially".format(nruns_seq))
    start = time.monotonic()
    for i in range(nruns):
        targ = (dataX, rdataY[i], model, params, weights)
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
    npts=dataX.shape[0]
    dataY= exp_one(dataX, A0, T0)
    exp_model = lmfit.Model(exp_one)
    params = exp_model.make_params(A=A0, T=T0)
    weights = np.full(dataX.shape, 1/sigma)
    npars=2
    #true_chisqr = sigma ** 2 * npts
    true_chisqr = npts
    true_redchi = true_chisqr/(npts-npars)
    print("true_chisqr= {:8.4f}".format(true_chisqr))
    print("true_redchi= {:8.6f}".format(true_redchi))

    noise_small= 1e-10
    print("Initial exact fit with weights = 1/sigma and noise = {}".format(noise_small))

    dataY_noise= add_random_noise(dataY, noise_small)
    all_args = (dataX, dataY_noise, exp_model, params, weights, False)
    fit_res= one_fit_with_weights_scalecovar(all_args)
    res_chisqr = fit_res.chisqr
    res_redchi = fit_res.redchi
    print("chisqr ={} redchi= {}".format(res_chisqr, res_redchi))

    print(fit_res.fit_report())
    covar = fit_res.covar
    #best = fit_res.best_values
    #print(" Fit params: A= {:8.6f} T= {:8.6f}".format(best['A'], best['T']))
    #print("True params: A= {:8.6f} T= {:8.6f}".format(A0, T0))
    print("COVAR =\n{}".format(covar))
    covar_redchi = covar*true_redchi
    #print("COVAR * true_redchi = \n{}".format(covar_redchi))
    param_stat=np.zeros((2,ntry))
    chisqr_stat=np.zeros((ntry))
    redchi_stat = np.zeros((ntry))

    print()
    print("Monte-Carlo covariance matrix estimation by {} fits ".format(ntry))
    for i in range(ntry):
        dataY_noise = add_random_noise(dataY, sigma)
        all_args = (dataX, dataY_noise, exp_model, params, weights, False)
        fit_res = one_fit_with_weights_scalecovar(all_args)
        best = fit_res.best_values
        chisqr_stat[i] = fit_res.chisqr
        redchi_stat[i] = fit_res.redchi
        if i==0:
            covar0=fit_res.covar
            print("chisqr ={:8.4f} redchi= {:8.6f}".format(chisqr_stat[i], redchi_stat[i]))
            print("real noise fit_report:")
            print(fit_res.fit_report())
            print("real noise COVAR =\n{}".format(covar0))
        param_stat[0, i] = best['A'] - A0
        param_stat[1, i] = best['T'] - T0
    print("Monte carlo finished")
    print("chisqr = {:8.4f}+/-{:8.4f}".format(np.mean(chisqr_stat), np.std(chisqr_stat)))
    print("redchi = {:8.6f}+/-{:8.6f}".format(np.mean(redchi_stat), np.std(redchi_stat)))
    mc_covar = np.cov(param_stat)
    print("MC_COVAR=\n{}".format(mc_covar))

    print("MC_COVAR/COVAR = \n{}".format(mc_covar/covar))

    return covar, mc_covar




# def fit_one_exp_to_two_exps(dataX, rdataYi, weights, rAT, model, params):
#     print()
#     print("Run one fit of two exps")
#     start = time.monotonic()
#     res= model.fit(rdataYi, params, x=dataX, weights=weights, method='least_squares', scale_covar=False)
#     finish = time.monotonic()
#     print("one fit finished after {} seconts, {} fits/sec".\
#           format(finish - start, 1/(finish - start)))
#     print(res.fit_report())
#     print(" Fit params= {}".format(str(res.best_values)))
#     print("True params= {{\'A\': {}, \'T\': {} }}".format(rAT[0], rAT[1]))
#     return res


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--one-fit', action='store_true', help='Run one fit of one exp')
    parser.add_argument('--fit-1to2', action='store_true', help='Run data exp1 to two exponents (excessive fit)')
    parser.add_argument('--fit-sequencially', action='store_true', help='Run multiple fits sequencially')
    parser.add_argument('--fit-parallel', action='store_true', help='Run multiple fits sequencially')
    parser.add_argument('--covar', action='store_true', help='Estimate covariance matrix from monte-carlo')
    args = parser.parse_args()

    npts = 128
    nruns_seq = 128
    ncpu = mp.cpu_count()
    nruns_par = 32 * ncpu
    nruns = max(nruns_seq, nruns_par)
    # ncpu=4
    npars = 2  # A and T in exp_one
    npars2 = 5 # A1, T1, A2, T2, c
    sigma = 0.01
    dataX = np.linspace(0, 3, npts)


    print("Generate data for tests")
    print("Generate exp_model")
    exp_model = lmfit.Model(exp_one)
    exp_two_model = lmfit.Model(exp_two_c)
    print("Generate exp_params")
    exp_params = exp_model.make_params(A=0.5, T=0.5)
    exp_two_params = exp_two_model.make_params(A1=0.25, T1=0.2, A2=0.25, T2=0.8, c=0)
    print("Generate random A and T values (rAT) of size {}".format(nruns))
    rAT=random_AT(nruns, npars)
    rAT2 = random_AT(nruns, npars2)
    print("Generate random_XY of size {}".format(rAT.shape[0]))
    rdata = random_XY(dataX, rAT, sigma)
    print("Data for tests ready")
    weights = np.full((npts), 1/sigma)

    if args.one_fit:
        irun=0
        res0 = run_one_fit(dataX, rdata[irun], weights, rAT[irun], exp_model, exp_params)

    if args.fit_1to2:
        irun=0
        res1 = run_one_fit(dataX, rdata[irun], weights, rAT[irun], exp_model, exp_params)
        rAT2[0, 0] = rAT[0, 0] # A1 = A
        rAT2[0, 1] = rAT[0, 1] # T1 = T
        rAT2[0, 2:] =0         # A2, T2, c = 0
        res21 = run_one_fit(dataX, rdata[irun], weights, rAT2[irun], exp_two_model, exp_two_params)

    if args.fit_sequencially:
        resseq= run_fits_sequencially(dataX, rdata, weights, rAT, exp_model, exp_params, nruns_seq)

    if args.fit_parallel:
        respar= run_fits_parallel(dataX, rdata, rAT, weights, exp_model, exp_params, nruns_par)

    if args.covar:
        print("==================================")
        print("tests with npts={}".format(npts))
        res_covar1 = run_monte_carlo_covar(dataX, 0.5, 0.5, 0.001, 1024)
        # res_covar2 = run_monte_carlo_covar(dataX, 0.5, 0.5, 0.005, 1024)
        # res_covar3 = run_monte_carlo_covar(dataX, 0.5, 0.5, 0.01, 1024)
        #
        # print("==================================")
        # npts = 1024
        # print("tests with npts={}".format(npts))
        # dataX = np.linspace(npts, 1, npts)
        # res_covar4 = run_monte_carlo_covar(dataX, 0.5, 0.5, 0.001, 1024)
        # res_covar5 = run_monte_carlo_covar(dataX, 0.5, 0.5, 0.005, 1024)
        # res_covar6 = run_monte_carlo_covar(dataX, 0.5, 0.5, 0.01, 1024)







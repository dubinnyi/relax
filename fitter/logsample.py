import numpy as np
import sys


class LogsamplerError(Exception):
    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return self.message


def calc_poly(p, t):
    # Calculate polynomial with array of coefficients
    # p - array of coefficients, shape (deg+1, K) or (deg+1,)
    # t - time, the argument of polynomial
    # result - array of shape (K,)
    n=p.shape[0] # degree of polynomial + 1
    if p.ndim == 2:
        poly=np.copy(p[0, :])
        for i in range(1, n):
            poly *= t
            poly += p[i, :]
    elif p.ndim == 1:
        poly= p[0]
        for i in range(1, n):
            poly *= t
            poly += p[i]
    else:
        raise LogsamplerError("Arrays with ndim>2 are not supported")

    return poly


def get_first_nonzero(data_1d):
    i1, t1 = 0, 0.0
    for i, d in enumerate(data_1d):
        if d != 0 or d != 0.0:
            i1, t1 = i, d
            break
    if t1 == 0 or t1 == 0.0:
        raise LogsamplerError("Time array have only zeroes. Could not logsample!")
    return i1, t1


def logsample(data, **kwargs):
    tstart = kwargs['tstart'] if 'tstart' in kwargs else 0
    dt     = kwargs['dt']     if 'dt'     in kwargs else 1
    deg    = kwargs['deg']    if 'deg'    in kwargs else 2
    factor = kwargs['factor'] if 'factor' in kwargs else 1.05
    time   = kwargs['time']   if 'time'   in kwargs else None

    if data.ndim == 2:
        (nd, nt)=data.shape
    elif data.ndim == 1:
        nd = 1
        nt =  data.shape[0]
    else:
        raise LogsamplerError("Arrays with ndim = {} >2 are not supported".format(data.ndim))
    datatr = np.transpose(data)
    if nt <= 1:
        return time, data
    if time:
        tend = time[-1]
    else:
        tend = tstart + nt * dt
        time = np.linspace(tstart, tend, nt, endpoint=False)

    lfirst, tfirst =get_first_nonzero(time)

    # time[1] should exist
    nlog, t = 1, tfirst
    while t < tend:
        t = t * factor
        if int(t/tfirst) > nlog:
            nlog += 1
    logdata = np.zeros((nd, nlog))
    logtime = np.zeros((nlog))
    l0, l1, ilog, t = 0, lfirst, 0, tfirst
    while t < tend*factor:
        t = t * factor
        l2 = int(t/tfirst)
        if l2 <= l1:
            continue
        #if int(t) > l0:
        #    break
        #print("(l0, l1) = ({},{})".format(l0,l1))
        subt = time[l0:l1]
        tmean = np.mean(subt)
        subdata = datatr[l0:l1,:] if data.ndim == 2 else datatr[l0:l1]
        deg_fit = min(subt.shape[0]-1,deg)
        #print('subt.shape = {}'.format(subt.shape))
        #print('subdata.shape = {}'.format(subdata.shape))
        p = np.polyfit(subt, subdata, deg=deg_fit)
        #print("p.shape = {}".format(p.shape))
        datamean = calc_poly(p, tmean)
        #print("datamean.shape = {}".format(datamean.shape))
        logtime[ilog] = tmean
        logdata[:, ilog] = datamean
        (l0, l1) = (l1, l2)
        if l1 > nt:
            l1 = nt
        ilog += 1
    if data.ndim == 1:
        logdata = logdata[0]
    return logtime, logdata

def test_logsample():
    import matplotlib.pyplot as plt
    nt= 100000
    nfunc= 3
    sigma = 0.05
    factor = 1.05

    data =  np.zeros((nfunc + 1, nt))
    noise = np.zeros((nfunc + 1, nt))
    t=np.linspace(0,nt-1,nt)

    #print(t)
    for f in range(nfunc+1):
        data[f,:]=np.exp(-np.copy(t)/(500*(f+1)))
        noise[f,:]=np.random.normal(0,sigma,nt)
    datanoise = data + noise
    #print(data)
    #################################################
    #
    ltime, ldata= logsample(datanoise, factor=factor)
    #
    #################################################

    #################################################
    # test for 1D array as input
    lt, ltd = logsample(data[0,:], factor=factor)
    print(ltd.shape)

    #print(ldata)
    print("size of logsamples data {}".format(ltime.shape[0]))

    fig, ax =plt.subplots(1, 2, figsize=(20, 10))
    ax[0].set_xscale('log')
    ax[0].set_title("{} linear points".format(nt))
    for f in range(nfunc+1):
        ax[0].plot(t, datanoise[f,:],'-')
    #ax[0].title('linear data')

    ax[1].set_xscale('log')
    ax[1].set_title("{} logsample points, factor={}".format(ltime.shape[0], factor))
    for f in range(nfunc + 1):
        ax[1].plot(ltime, ldata[f, :],'-')
    #ax[0].title('LOG samples data')
    plt.show()

    fig, ax = plt.subplots(figsize=(20, 10))
    ax.set_xscale('log')
    ax.set_title("{} linear points vs {} logsample ponts, noise={}".format(nt, ltime.shape[0], sigma))
    ax.plot(t, data[0,:] + noise[0,:], '-')
    ax.plot(ltime, ldata[0, :], 'o-')
    plt.show()

    ltime, ldata = logsample(data, factor=factor)

    fig, ax = plt.subplots(figsize=(20, 10))
    ax.set_xscale('log')
    ax.set_title("exact exp(-t/500) vs {} logsample ponts".format(nt, ltime.shape[0]))
    tlogt=10.**np.linspace(0,5,1000)
    texp=np.exp(-np.copy(tlogt)/(500))
    ax.plot(tlogt, texp, '-')
    ax.plot(ltime, ldata[0, :], 'o-')
    plt.show()


    plt.close()


if __name__ == '__main__':
    test_logsample()


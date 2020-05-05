import numpy as np


def calc_poly(p, t):
    # Calculate polynomial with array of coefficients
    # p - array of coefficients, shape (deg+1, K)
    # t - time, the argument of polynomial
    # result - array of shape (K,)
    n=p.shape[0] # degree of polynomial + 1
    poly=np.copy(p[0,:])
    for i in range(1,n):
        poly *= t
        poly += p[i,:]
    return poly

def logsample(data, **kwargs):
    dt=     kwargs['dt']     if 'dt'     in kwargs else 1
    deg=    kwargs['deg']    if 'deg'    in kwargs else 2
    factor= kwargs['factor'] if 'factor' in kwargs else 1.05

    (nd, nt)=data.shape
    datatr = np.transpose(data)
    tend = dt * nt
    time = np.linspace(0, tend, nt, endpoint=False)
    nlog, t = 1, dt
    while t< tend:
        t= t * factor
        if int(t) > nlog:
            nlog+= 1
    logdata= np.zeros((nd,nlog))
    logtime= np.zeros((nlog))
    l0, l1, ilog, t = 0, 1, 0, dt
    while t< tend*factor:
        t = t * factor
        l2 = int(t)
        if l2 <= l1:
            continue
        #if int(t) > l0:
        #    break
        #print("(l0, l1) = ({},{})".format(l0,l1))
        subt= time[l0:l1]
        tmean= np.mean(subt)
        subdata= datatr[l0:l1,:]
        deg_fit = min(subt.shape[0]-1,deg)
        #print('subt.shape = {}'.format(subt.shape))
        #print('subdata.shape = {}'.format(subdata.shape))
        p = np.polyfit(subt, subdata, deg=deg_fit)
        #print("p.shape = {}".format(p.shape))
        datamean= calc_poly(p, tmean)
        #print("datamean.shape = {}".format(datamean.shape))
        logtime[ilog]= tmean
        logdata[:,ilog]= datamean
        (l0, l1)= (l1, l2)
        if l1> nt:
            l1= nt
        ilog+= 1
    return logtime, logdata

def test_logsample():
    import matplotlib.pyplot as plt
    nt= 100000
    nfunc= 3
    data =  np.zeros((nfunc + 1, nt))
    noise = np.zeros((nfunc + 1, nt))
    t=np.linspace(0,nt-1,nt)
    sigma = 0.05
    #print(t)
    for f in range(nfunc+1):
        data[f,:]=np.exp(-np.copy(t)/(500*(f+1)))
        noise[f,:]=np.random.normal(0,sigma,nt)
    datanoise = data + noise
    #print(data)
    factor=1.05
    #################################################
    #
    ltime, ldata= logsample(datanoise, factor=factor)
    #
    #################################################
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


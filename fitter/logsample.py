import numpy as np

def logsample(dt, data, factor= 1.05, deg=2):
    (nd,nt)=data.shape
    datatr = np.transpose(data)
    tend = dt * nt
    time = np.linspace(0, tend, nt, endpoint=False)
    nlog, t = 1, 1.00
    while t< tend:
        t= t * factor
        if int(t) > nlog:
            nlog+= 1
    logdata= np.zeros((nd,nlog))
    logtime= np.zeros((nlog))
    l0, l1, t = 0, 1, 1.00
    while t< tend:
        t = t * factor
        if int(t) <= l1:
            continue
        subt= time[l0:l1]
        nsubt= subt.shape[0]
        tmean= np.mean(subt)
        subdata= datatr[l0:l1,:]
        deg_fit = min(nsubt-1,deg)
        p = np.polyfit(subt, subdata, deg=deg_fit)
        print("p.shape = {}".format(p.shape))
        continue
        datamean= np.poly1d(p)(tmean)
        logtime[l0]= tmean
        logdata[l0]= datamean
        (l0, l1) = (l1, int(t))
    return logtime, np.transpose(logdata)


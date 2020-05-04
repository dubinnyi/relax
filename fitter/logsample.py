import numpy as np

def calc_poly(p, t):
    # Calculate polynomial
    n=p.shape[0] # degree of polynomial + 1
    poly=np.copy(p[0,:])
    for i in range(1,n):
        poly *= t
        poly += p[i,:]
    return poly

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
    l0, l1, ilog, t = 0, 1, 0, 1.00
    while t< tend*factor:
        t = t * factor
        if int(t) <= l1:
            continue
        #if int(t) > l0:
        #    break
        print("(l0, l1) = ({},{})".format(l0,l1))
        subt= time[l0:l1]
        nsubt= subt.shape[0]
        tmean= np.mean(subt)
        subdata= datatr[l0:l1,:]
        deg_fit = min(nsubt-1,deg)
        #print('subt.shape = {}'.format(subt.shape))
        #print('subdata.shape = {}'.format(subdata.shape))
        p = np.polyfit(subt, subdata, deg=deg_fit)
        #print("p.shape = {}".format(p.shape))
        datamean= calc_poly(p, tmean)
        #print("datamean.shape = {}".format(datamean.shape))
        logtime[ilog]= tmean
        logdata[:,ilog]= datamean
        (l0, l1)= (l1, int(t))
        if l1> nt:
            l1= nt
        ilog+= 1
    return logtime, logdata

def test_logsample():
    nt= 100
    nfunc= 3
    data=np.zeros((nfunc,nt))
    t=np.linspace(0,nt-1,nt)
    print(t)
    for f in range(nfunc):
        data[f,:]=np.copy(t)**f
    print(data)
    logdata=logsample(1.,data)
    print(logdata)

if __name__ == '__main__':
    test_logsample()


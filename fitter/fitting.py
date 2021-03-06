import sys
import h5py

import numpy as np
import copy as c
import matplotlib.pyplot as plt

from fitter.exp_model import CModel
from fitter.fit_res import FitResult
from fitinfo import FitInfo

BASE_VAL = np.array([0.1, 1, 0.01, 10, 0.01, 50, 0.01,
                     100, 0.01, 1000, 0.01, 2000, 0.01,
                     3000, 0.01, 4000, 0.01, 5000, 0.01])
BASE_KEY = ('c', 'adecay', 'aamplitude', 'bdecay', 'bamplitude', 'cdecay', 'camplitude',
            'ddecay', 'damplitude', 'edecay', 'eamplitude', 'fdecay', 'famplitude',
            'gdecay', 'gamplitude','hdecay', 'hamplitude','idecay', 'iamplitude')

rndmizer = np.random.RandomState()

class Fitter:
    def __init__(self, minexp=4, maxexp=6, randFactor=(.2, 5), ntry=5, logger=print):
        self.model = None
        self.ntry  = ntry
        self.randFactor  = randFactor
        self.expInterval = (minexp, maxexp)

        self.name_string = "Unnamed data"
        self.data = None
        self.std  = None
        self.time = None

        self.cexp = 0
        self.params  = None
        self.lastFit = None
        self.init_values = None
        self.lastSuccess = False

        self.res = None

        self.bestResults = [None] * self.nexp
        self.anyResult = False
        self.fitInfos = [None] * self.nexp
        self.fitResult = logger

    ## Iterators
    def exp_iter(self):
        for exp in range(self.expInterval[0], self.expInterval[1] + 1):
            yield exp

    ## Getters
    def get_expInterval(self):
        return self.expInterval

    @property
    def nexp(self):
        return self.expInterval[1] + 1 - self.expInterval[0]


    ## Setters
    @nexp.setter
    def nexp(self, minexp, maxexp):
        self.expInterval = (minexp, maxexp)
        self.bestResults = [None] * (maxexp + 1 - minexp)
        self.prep_model()

    def set_time(self, timeline=None, dt=None, nframe=None):
        if timeline:
            self.time = timeline
        elif dt and nframe:
            self.time = np.array([i*dt for i in range(nframe)])
        else:
            print('ERROR!! Missing arguments. Please set timeline or dt with number of frames', file=sys.stderr)

    def set_ntry(self, ntry):
        self.ntry = ntry

    def set_randomFactor(self, randFactor):
        self.randFactor = randFactor


    ## Prepare to Fit

    def prep_model(self):
        self.cexp = self.expInterval[0]
        self.model = CModel(self.expInterval[0])
        self.init_values = dict(zip(BASE_KEY[:(2*self.nexp + 1)], c.copy(BASE_VAL[:(2*self.nexp + 1)])))


    def fit(self, data, std, timeline, method='NexpNtry', *args, **kwargs):
        self.clear()
        self.data = data
        self.std = std
        self.time = timeline
        self.name_string = "Unnamed data" if not 'name_string' in kwargs else kwargs['name_string']
        if method == 'NexpNtry':
            self.fit_NtryNexp(*args, **kwargs)
        else:
            print('ERROR!! Method should be NexpNtry', file=sys.stderr)

        return self.bestResults

    def _fit(self, init_values=None):
        #if self.model.nexp > 4:
        #    return
        #################
        y = self.data
        length = y.shape[0]
        x = self.time
        #################
        self.lastFit = self.model.fit(y, x=x, method='least_squares', weights=1/self.std, nan_policy='omit', **init_values)

    def fit_NtryNexp(self, **kwargs):
        self.prep_model()

        for self.cexp in self.exp_iter():
            self.fit_ntry()
            try:
                if not self.res:
                    self.res = self.lastFit

                elif self.res.chisqr > self.lastFit.chisqr:
                    self.res = self.lastFit

                if self.cexp == self.expInterval[1]:
                    self.save_result()
                    if self.res:
                        self.anyResult = True
                        print("{}: Best CHISQR = {:8.4f}".format(self.name_string, self.res.chisqr))
                    else:
                        print("{}: NO RESULT FOUND".format(self.name_string))
                    return self.res
            except AttributeError as e:
                print("{}: ERROR!! res is None.".format(self.name_string))
                print("Error is {}".format(e))
                print("It happend while fitting {} exponents. With those initial values: {}".\
                      format( self.cexp, self.init_values), file=sys.stderr)
                self.lastSuccess = False
                return
            self.save_result()
            self.clean_beforeFit()
            self.model.add_exp()
            self.init_values = dict(zip(BASE_KEY[:(2*self.cexp + 1)], c.copy(BASE_VAL[:(2*self.cexp + 1)])))
        return self.res

    def fit_ntry(self):
        curBestFit = None

        for itry in range(self.ntry):
            with FitInfo(self.cexp, output=self.fitResult) as fi:
                self._fit(self.init_values)
                fi.add_successRate(self.model.has_covar())

            name_string_exp_try = "{} exp{:<2} - try{:<2}".\
                format(self.name_string, self.cexp, itry + 1)
            chi_sqr_string = "CHISQR= {:8.4f}".format(self.lastFit.chisqr)
            info_string = ""
            if not self.model.has_covar():
                info_string = "-- No covariance matrix in result"
            elif not curBestFit:
                curBestFit = self.lastFit
            elif curBestFit and curBestFit.chisqr > self.lastFit.chisqr:
                curBestFit = self.lastFit
                info_string = "-- New BEST"

            if curBestFit:
                self.lastSuccess = True

            print("{}: {} {}". format(name_string_exp_try, chi_sqr_string, info_string))
            self.change_init()
        self.lastFit = curBestFit

    def change_init(self):
        rndmizer.seed()
        new_val = c.copy(BASE_VAL)
        new_val[1::2] = new_val[1::2] * rndmizer.uniform(*self.randFactor)
        self.init_values = dict(zip(BASE_KEY[:(2*self.cexp + 1)], new_val[:(2*self.cexp + 1)]))

    def save_result(self):
        if self.lastSuccess and self.res:
            stats = {'aic': self.res.aic, 'chisqr': self.res.chisqr, 'bic': self.res.bic,
                    'redchi': self.res.redchi}

            data = {'model': self.res.model, 'params': self.res.best_values,
                    'stats': stats, 'covar': self.res.covar, 'success': self.lastSuccess,
                    'init_values': self.res.init_values, 'nexp': self.nexp}
        else:
            model = self.res.model if self.res else None
            init_values = self.res.init_values if self.res else {}
            data = {'success': self.lastSuccess, 'model': model,
                    'init_values': init_values, 'nexp': self.nexp}
        self.bestResults[self.cexp - self.expInterval[0]] = FitResult(**data)

    # Savings and Results

    def plot_fit(self, name):
        fig = plt.figure(1)
        # self.res.model_fit.plot()
        # step = self.time
        times=self.time
        length = self.data.shape[0]
        # times = np.arange(0, length*step, step)
        x = (times + 1e-16) / 1000
        # plt.xticks(times, x)
        # errticks = x[:3000] + x[3000::10000]
        plt.subplot(211)
        ##################################################
        plt.errorbar(x[::10000], self.data[::10000], yerr=self.std[::10000], fmt='none')
        ##################################################
        plt.plot(x, self.data, 'c-', label='init data')
        plt.plot(x, self.res.best_fit, 'r-', label='best fit')
        plt.xlabel('t, ns')
        plt.ylabel('C(t)')
        plt.legend()
        plt.subplot(212)
        ##################################################
        plt.errorbar(x[:1000:100], self.data[:1000:100], yerr=self.std[:1000:100], fmt='none')
        plt.plot(x[:1000:100], self.data[:1000:100], 'c-', label='init data')
        plt.plot(x[:1000:100], self.res.best_fit[:1000:100], 'r-', label='best fit')
        ##################################################
        plt.xlabel('t, ns')
        plt.ylabel('C(t)')
        plt.legend()
        ##################################################
        # cres = self.group.res
        plt.savefig('exp{}.png'.format(name))
        ###################################################
        plt.close()

    def get_result(self):
        return self.res.report()

    def clean_beforeFit(self):
        self.lastSuccess = False

    def clear(self):
        self.data = None
        self.std = None
        self.time = None

        self.cexp = 0
        self.res = None
        self.params = None
        self.init_values = None
        self.lastFit = None
        self.lastSuccess = False
        self.bestResults = [None] * self.nexp

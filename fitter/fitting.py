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
        self.init_values = None

        self.bestResults = [None] * self.nexp
        self.fitInfos = [None] * self.nexp
        self.logger = logger

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
        return self.model.fit(y, x=x, method='least_squares', weights=1/self.std, nan_policy='omit', **init_values)

    def fit_NtryNexp(self, **kwargs):
        self.prep_model()
        bestFit_ntry = None
        success_ntry = False
        for self.cexp in self.exp_iter():
            fit_ntry, success_ntry = self.fit_ntry()
            try:
                if not bestFit_ntry:
                    bestFit_ntry = fit_ntry

                elif bestFit_ntry.chisqr > fit_ntry.chisqr:
                    bestFit_ntry = fit_ntry

                if self.cexp == self.expInterval[1]:
                    self.save_result(fit_ntry, success_ntry)
                    if bestFit_ntry:
                        print("{}: Best CHISQR = {:8.4f}".format(self.name_string, bestFit_ntry.chisqr))
                    else:
                        print("{}: NO RESULT FOUND".format(self.name_string))
            except AttributeError as e:
                print("{}: ERROR!! res is None.".format(self.name_string))
                print("Error is {}".format(e))
                print("It happend while fitting {} exponents. With those initial values: {}".\
                      format(self.cexp, self.init_values), file=sys.stderr)
                success_ntry = False
                return
            self.save_result(fit_ntry, success_ntry)
            self.model.add_exp()
            self.init_values = dict(zip(BASE_KEY[:(2*self.cexp + 1)], c.copy(BASE_VAL[:(2*self.cexp + 1)])))

    def fit_ntry(self):
        bestFit_once = None
        success_once = False

        for itry in range(self.ntry):
            with FitInfo(self.cexp, output=self.logger) as fi:
                fit_once = self._fit(self.init_values)
                ## Проверить можно ли иначе проверять наличие ковариационной матрицы
                fi.add_successRate(self.model.has_covar())

            name_string_exp_try = "{} exp{:<2} - try{:<2}".\
                format(self.name_string, self.cexp, itry + 1)
            chi_sqr_string = "CHISQR= {:8.4f}".format(fit_once.chisqr)
            info_string = ""
            if not self.model.has_covar():
                info_string = "-- No covariance matrix in result"
            elif not bestFit_once:
                bestFit_once = fit_once
            elif bestFit_once and bestFit_once.chisqr > fit_once.chisqr:
                bestFit_once = fit_once
                info_string = "-- New BEST"

            if bestFit_once:
                success_once = True

            print("{}: {} {}". format(name_string_exp_try, chi_sqr_string, info_string))
            self.change_init()
        return bestFit_once, success_once

    def change_init(self):
        rndmizer.seed()
        new_val = c.copy(BASE_VAL)
        new_val[1::2] = new_val[1::2] * rndmizer.uniform(*self.randFactor)
        self.init_values = dict(zip(BASE_KEY[:(2*self.cexp + 1)], new_val[:(2*self.cexp + 1)]))

    def save_result(self, result, successRate):
        if successRate and result:
            stats = {'aic': result.aic, 'chisqr': result.chisqr, 'bic': result.bic,
                    'redchi': result.redchi}

            data = {'model': result.model, 'params': result.best_values,
                    'stats': stats, 'covar': result.covar, 'success': successRate,
                    'init_values': result.init_values, 'nexp': self.nexp}
        else:
            model = result.model if result else None
            init_values = result.init_values if result else {}
            data = {'success': successRate, 'model': model,
                    'init_values': init_values, 'nexp': self.nexp}

        self.bestResults[self.cexp - self.expInterval[0]] = FitResult(**data)

    # Savings and Results

    def plot_fit(self, name, result):
        fig = plt.figure(1)
        # result.model_fit.plot()
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
        plt.plot(x, result.best_fit, 'r-', label='best fit')
        plt.xlabel('t, ns')
        plt.ylabel('C(t)')
        plt.legend()
        plt.subplot(212)
        ##################################################
        plt.errorbar(x[:1000:100], self.data[:1000:100], yerr=self.std[:1000:100], fmt='none')
        plt.plot(x[:1000:100], self.data[:1000:100], 'c-', label='init data')
        plt.plot(x[:1000:100], result.best_fit[:1000:100], 'r-', label='best fit')
        ##################################################
        plt.xlabel('t, ns')
        plt.ylabel('C(t)')
        plt.legend()
        ##################################################
        # cres = self.group.res
        plt.savefig('exp{}.png'.format(name))
        ###################################################
        plt.close()

    def clear(self):
        self.data = None
        self.std = None
        self.time = None

        self.cexp = 0
        self.params = None
        self.init_values = None
        self.bestResults = [None] * self.nexp

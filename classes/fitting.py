import numpy as np
import matplotlib.pyplot as plt

from classes.exp_model import CModel

BASE_VAL = np.array([0.1, 1, 0.01, 10, 0.01, 50, 0.01, 100, 0.01, 1000, 0.01, 3000, 0.01])
BASE_KEY = ['c', 'adecay', 'aamplitude', 'bdecay', 'bamplitude', 'cdecay', 'camplitude', 'ddecay', 'damplitude', 'edecay', 'eamplitude', 'fdecay', 'famplitude']

class Fitting:
    """docstring for Accf"""
    def __init__(self, data, std, step):
        self.data = data
        self.std = std
        self.res = None
        self.model = None
        self.params = None
        self.time = step
        self.init_values = None
        self.nexp = 0

        self.tmp = None

    def add_model(self, nexp):
        self.nexp = nexp
        self.model = CModel(nexp)
        self.init_values = dict(zip(BASE_KEY[:(2*self.nexp + 1)], BASE_VAL[:(2*self.nexp + 1)]))

    def _fit(self, init_values=None):
        #if self.model.nexp > 4:
        #    return
        #################
        y = self.data
        length = y.shape[0]
        x = self.time
        #################
        self.params = self.model.prep_params()
        self.tmp = self.model.fit(y, self.params, x=x, method='least_squares', weights=1/self.std, nan_policy='omit', **init_values)

    def fit(self, init_values=None):
        while (self.fit10()):
            self.res = self.tmp
            if self.nexp == 6:
                return self.res
            self.model.add_exp()
            self.nexp += 1
            self.init_values = dict(zip(BASE_KEY[:(2*self.nexp + 1)], BASE_VAL[:(2*self.nexp + 1)]))
        return self.res


    def fit10(self):
        for _ in range(10):
            self._fit(self.init_values)
            if not self.model.has_covar():
                self.change_init()

            # elif self.nexp == 6 and self.model.has_covar() and self.tmp.chisqr < 1:
            #      self.change_init()
            else:
                return True
        return False

    def change_init(self):
        new_val = BASE_VAL
        new_val[1::2] = BASE_VAL[1::2] * np.random.uniform(.2, 5)
        self.init_values = dict(zip(BASE_KEY[:(2*self.nexp + 1)], new_val[:(2*self.nexp + 1)]))

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

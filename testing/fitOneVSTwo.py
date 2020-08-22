#!/usr/bin/python3 -u

import numpy as np
from lmfit.models import ExponentialModel, ConstantModel

Prefixes = {
    1:'a',
    2:'b',
    3:'c',
    4:'d',
    5:'e',
    6:'f'
}

def f1(x, a, b, c):
#     print('q', end='')
    return a * np.exp(-b * x) + c

def f2(x, a, b, c, d, e):
#     print('q', end='')
    return a * np.exp(-b * x) + c*np.exp(-d * x) + e

def data_gen(f, params):
    x = np.linspace(0, 5, 10000)
    y = f(x,*params) + 0.01*np.random.normal(0.02, size=len(x))
    return x, y


def prepare_model(nexp):
    emodel = ConstantModel() + ExponentialModel(prefix='a') + ExponentialModel(prefix='b')
    pars.add('e', value=0, min=0)
    pars.add('cntrl', value=1, min=1-1e-5, max=1+1e-5)
    pars['cntrl'].expr = 'c'
    pars['cntrl'].vary = True

    expr = '{}amplitude'
    all_expr = ''
    for i in range(1, 1):
        pars['cntrl'].expr += ' + ' + expr.format(Prefixes[i])
    return emodel, pars




parameters2 = [0.7, 0.6, 0.2, 0.4, 0.1]
parameters1 = [0.7, 0.6, 0.3]

x, y = data_gen(f1, parameters1)
emodel, params = prepare_model()
res = emodel.fit(y, x=x, params, method='least_squares')


import numpy as np

from lmfit.models import ConstantModel, ExponentialModel
from lmfit import Model


def exp(x, A, T):
    return A*np.exp(-T*x)


class CModel(Model):
    """docstring for CModel"""
    def __init__(self, nexp=0, moddef=" "):
        self.definition = moddef
        self.model = ConstantModel()
        self.nexp = 0
        self.errors = None
        self.res = None
        for _ in range(nexp):
            self.add_exp()

    def add_exp(self):
        self.nexp += 1
        self.model += ExponentialModel(prefix=Prefixes[self.nexp])

    def prep_params(self):
        amp = '{}amplitude'
        dec = '{}decay'
        cntrl_expr = 'c'
        self.model.set_param_hint('c', value=1.0, min=0)
        for i in range(1, self.nexp + 1):
            currA = amp.format(Prefixes[i])
            currT = dec.format(Prefixes[i])
            self.model.set_param_hint(currA, value=1.0, min=0)
            self.model.set_param_hint(currT, value=1.0, min=0)
            cntrl_expr += ' + ' + currA

        pars = self.model.make_params()
        pars.add('cntrl', value=1, min=1-1e-5, max=1+1e-5)
        pars['cntrl'].vary = True
        pars['cntrl'].expr = cntrl_expr
        return pars

    def fit(self, *args, **kwargs):
        try:
            self.res = self.model.fit(*args, **kwargs)
        except Exception as e:
            print("Undefined exception while fit: {} {}".format(type(e), e))
            raise
        return self.res

    def has_covar(self):
        covar = self.res.covar
        if covar is None or np.isnan(np.sum(covar)):
            return False
        else:
            return True

    def report(self):
        return self.res.fit_report(), self.res.covar


Prefixes = {
    1: 'a',
    2: 'b',
    3: 'c',
    4: 'd',
    5: 'e',
    6: 'f'
}

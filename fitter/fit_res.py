import os
import sys
import h5py

import numpy as np
import utils as u


class FitResult():
    def __init__(self, model=None, init_values=None, params=None,
                 covar=None, stats=None, nexp=None, succes=None):
        self._nexp = nexp
        self._model = model
        self._init_values = init_values

        self._param_names = list(params.keys()) if params else None
        self._param_vals = np.array(list(params.values())) if params else None
        self._param_errs = None

        self._covar = covar
        self._stats = stats
        self.succes = succes

    def __post_init__(self):
        self._param_errs = np.sqrt(np.diag(self._covar))


    def calc_paramErrs(self):
        self._param_errs = np.sqrt(np.diag(self._covar))

    # Getters
    @property
    def nexp(self):
        return self._nexp

    @nexp.setter
    def nexp(self, nexp):
        self._nexp = nexp

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, model):
        self._model = model

    @property
    def initialValues(self):
        return self._init_values

    @initialValues.setter
    def initialValues(self, init_values):
        self._init_values = init_values

    @property
    def param_vals(self):
        return self._param_vals

    @param_vals.setter
    def param_vals(self, param_vals):
        self._param_vals = param_vals()

    @property
    def covar(self):
        return self._covar

    @covar.setter
    def covar(self, covar_matrix):
        self._covar = covar_matrix

    @property
    def paramErrors(self):
        if not self._param_errs:
            self.calc_paramErrs()
        return self._param_errs

    @property
    def stats(self, stat=None):
        if not stat:
            return self._stats
        elif stat in self._stats.keys():
            return self._stats[stat]
        else:
            print('ERROR!! there no {} in fit statistic'.format(stat), file=sys.stderr)

    # Savings

    # type - type of file which would be used for saving [npy, hdf]
    def toFile(self, file, ftype='npy'):
        fid, own_fid = u.get_fid(file, ftype, 'w')

        if ftype == 'hdf5':
            self.save_hdf(fid)
        elif ftype == 'npy':
            self.save_npy(fid)


        if own_fid:
            fid.close()

    def save_hdf(self, fid):
        grp = fid.create_group()
        grp.create_dataset('params', data=self.params)
        grp.create_dataset('covar', data=self.best_covar)
        for key, val in self.stats.items():
            grp.attrs.create(key, val)

    def save_npy(self, fid):
        #TODO
        pass

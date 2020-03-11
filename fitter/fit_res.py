import os
import sys
import h5py

import numpy as np


class FitResult():
    def __init__(self, model=None, init_values=None, params=None, covar=None, stats=None, nexp=None):
        self.nexp = nexp
        self.model = model
        self.init_values = init_values

        self.parameters = params
        self.param_errs = None

        self.best_covar = covar
        self.stats = stats


    def calc_paramErrs(self):
        self.param_errs = np.sqrt(np.diag(self.covar))

    # Getters
    def get_nexp(self):
        return self.nexp

    def get_model(self):
        return self.model

    def get_initialValues(self):
        return self.init_values

    def get_params(self):
        return self.parameters

    def get_covar(self):
        return self.best_covar

    def get_paramErrors(self):
        if not self.param_errs:
            self.calc_paramErrs()
        return self.param_errs

    def get_stats(self, stat=None):
        if not stat:
            return self.stats
        elif stat in self.stats.keys():
            return self.stats[stat]
        else:
            print('ERROR!! there no {} in fit statistic'.format(stat), file=sys.stderr)

    # Savings

    # type - type of file which would be used for saving [npy, hdf]
    def toFile(self, file, ftype='npy'):
        own_fid = False
        if isinstance(file, basestring):
            if not file.endswith('.{}'.format(ftype)):
                file = file + '.{}'.format(ftype)
            if ftype == 'npy':
                fid = open(file, "wb")
            elif ftype == 'hdf5':
                fid = h5py.File(file, 'w')
            own_fid = True
        elif is_pathlib_path(file):
            if not file.name.endswith('.'.format(ftype)):
                file = file.parent / (file.name + '.{}'.format(ftype))
            if ftype == 'npy':
                fid = file.open("wb")
            elif ftype == 'hdf5':
                fid = h5py.File(file, 'w')
            own_fid = True
        else:
            fid = file

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

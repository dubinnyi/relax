import os
import sys
import h5py

import numpy as np
import pandas as pd
import utils as u


class Counter:
    def __init__(self):
        # self.dataInfo = ['group', 'tcf', 'fit method', 'exponent count', 'success count', 'fail count', 'mean time', 'all time']
        self.dataInfo = ['group', 'tcf', 'fit method', 'exponent count', 'success rate', 'fit time']
        self.data = pd.DataFrame(columns=self.dataInfo)

        self.cgroup = None
        self.ctcf = None
        self.cmethod = None

    ## Adders
    def add_fitInfo(self, fitInfo_series=None, expCount=None, successRate=None, time=None):
        if fitInfo_series:
            self.data = self.data.append(pd.Series(data={'group': self.cgroup,
               'tcf': self.ctcf,
               'fit method': self.cmethod,
               'exponent count': fitInfo_series.expCount,
               'success rate': fitInfo_series.successRate,
               'fit time': fitInfo_series.fitTime}), ignore_index=True)
        else:
            self.data = self.data.append(pd.Series(data={'group': self.cgroup,
               'tcf': self.ctcf,
               'fit method': self.cmethod,
               'exponent count': expCount,
               'success rate': successRate,
               'fit time': time}), ignore_index=True)

    def set_curGroup(self, cgroup):
        self.cgroup = cgroup

    def set_curTcf(self, ctcf):
        self.ctcf = ctcf

    def set_curMethod(self, cmethod):
        self.cmethod = cmethod

    def clean(self):
        pass

    def save(self, filename):
        self.data.to_csv(filename, index=False)

    # def add_successRate(self, sucRate):
        # pass

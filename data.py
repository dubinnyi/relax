import os
import sys
import h5py

import numpy as np
import utils as u


class Data:
    def __init__(self, data, errors, timeline=None, dt=None, nframe=None, filename=None, filepath=None, host=None, ntrace=None, tcf=None, proteinName=None, aminoAcid=None, aShort=None, aFull=None, relaxGroup=None, traces=None):
        # Where data from
        self.filename = filename if filename else 'NaN'
        self.filePath = filepath if filepath else 'Nan'
        self.host = host if host else 'NaN'
        self.ntrace = ntrace if ntrace else 0
        self.traces = traces if traces else None
        self.tcf = tcf.lower() if tcf else ''

        # Protein info
        self.proteinName = proteinName if proteinName else'NaN'
        self.aminoAcid = aminoAcid if aminoAcid else 'NaN'

        self.aShort = aShort if aShort else []
        self.aFull  = aFull if aFull else []

        self.rGroup = relaxGroup if relaxGroup else 'NaN'

        # Data
        self.time = self.setTime(timeline, dt, nframe)
        self.dataCF = self.setData(data)
        self.errors = errors

    # Setters
    def setTime(self, timeline=None, dt=None, nframe=None):
        if timeline:
            self.time = timeline
        elif dt and nframe:
            self.time = np.array([i*dt for i in range(nframe)])
        else:
            print('ERROR!! Missing arguments. Please set timeline or dt with number of frames', file=sys.stderr)

    def setData(self, data):
        if len(data.shape) == 1:
            self.dataCF = data.reshape(1, *data.shape)
        else:
            self.dataCF = data

    def setErrors(self, errs):
        if len(errs.shape) == 1:
            self.errors = errs.reshape(1, *errs.shape)
        else:
            self.errors = errs

    def setTraces(self, traces):
        self.traces = traces
        self.ntrace = len(traces)

    # Iterators


    # Readers

    def read_fromFile(self, file, ftype, fields=None):
        fid, own_fid = u.get_fid(file, ftype, 'r')







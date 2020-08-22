import re
import h5py
import numpy as np


# filename_re = re.compile(r'^(?P<filename>\S+\.hdf5?)(?P<path_in_file>\/\S+)?$')

# ftype - [npy, hdf, csv]
# perm -  [w, r, r+(not for npy)]
def get_fid(file, ftype, perm):
    own_fid = False
    if isinstance(file, basestring):
        if not file.endswith('.{}'.format(ftype)):
            file = file + '.{}'.format(ftype)
        if ftype == 'npy':
            fid = open(file, "{}b".format(perm))
        elif ftype == 'hdf':
            fid = h5py.File(file, perm)
        elif ftype == 'csv':
            fid = open(file, perm)

        own_fid = True
    elif is_pathlib_path(file):
        if not file.name.endswith('.'.format(ftype)):
            file = file.parent / (file.name + '.{}'.format(ftype))
            if ftype == 'npy':
                fid = file.open("{}b".format(perm))
            elif ftype == 'hdf':
                fid = h5py.File(file, perm)
            elif ftype == 'csv':
                fid = file.open(perm)
        own_fid = True
    else:
        fid = file
    return fid, own_fid

def open_folderInHdf(fd, path):
    return fd[path]


# def get_filenamePath(filename):
#     if filename_re.search(filename):
#         res = filename_re.match(filename)
#         fname = res['filename']
#         path = res['path_in_file']
#         return fname, path


def splitCamelCase(name, toLowerCase=True):
    found = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', name))
    if toLowerCase:
        found = found.lower()
    return found.split()

def create_nameArray(shape, namesList, dtype=float):
    ds_dt = np.dtype({'names':namesList,'formats':[dtype]*len(namesList) })
    data = np.zeros((len(namesList), shape))
    rec_arr = np.rec.fromarrays(data, dtype=ds_dt)
    return rec_arr

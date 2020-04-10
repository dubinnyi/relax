import re
import h5py


# ftype - [npy, hdf5, csv]
# perm -  [w, r]
def get_fid(file, ftype, perm):
    own_fid = False
    if isinstance(file, basestring):
        if not file.endswith('.{}'.format(ftype)):
            file = file + '.{}'.format(ftype)
        if ftype == 'npy':
            fid = open(file, "{}b".format(perm))
        elif ftype == 'hdf5':
            fid = h5py.File(file, perm)
        elif ftype == 'csv':
            fid = open(file, perm)

        own_fid = True
    elif is_pathlib_path(file):
        if not file.name.endswith('.'.format(ftype)):
            file = file.parent / (file.name + '.{}'.format(ftype))
            if ftype == 'npy':
                fid = file.open("{}b".format(perm))
            elif ftype == 'hdf5':
                fid = h5py.File(file, perm)
            elif ftype == 'csv':
                fid = file.open(perm)
        own_fid = True
    else:
        fid = file
    return fid, own_fid


def splitCamelCase(name, toLowerCase=True):
    found = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', name))
    if toLowerCase:
        found = found.lower()
    return found.split()

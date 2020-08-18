#!/usr/pin/python3 -u

import sys

import numpy as np

from h5py import File, Group


class hdfError(Exception):
    def __init__(self, msg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msg = msg

    def __str__(self):
        return self.msg


class hdfAPI(File):
    """docstring for Hdf_API"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trj_list = []
        self.tcf_list = []
        self.grp_list = []

    ### Iterators

    def trj_iter(self):
        for key, item in self['/'].items():
            yield key, item

    # use 'acf' or 'ccf' to iterate trough
    # tcf groups in file
    def tcf_iter(self, tcf=''):
        if tcf:
            for _, item in self.trj_iter():
                yield item[tcf]
        else:
            for _, item in self.trj_iter():
                for tcf in ['acf', 'ccf']:
                    return item[tcf]

    def group_iter(self, tcf='', gname='', all=False):
        if not all:
            trj = self._get_zeroTrj()
            if gname in trj[tcf].keys():
                yield trj[tcf][gname]
                return

        groups = [gname] if gname else self.get_groupList()
        for gname in groups:
            if tcf:
                for item in self.tcf_iter(tcf):
                    if gname in item.keys():
                        g = item[gname]
                        yield g
            else:
                for item in self.tcf_iter():
                    if gname in item.keys():
                        g = item[gname]
                        yield g

    ### Getters

    def get_time(self):
        item = self._get_zeroTrj()
        if 't' in item['acf'].keys():
            return np.array(item['acf']['t'])
        elif 'time' in item['acf'].keys():
            return np.array(item['acf']['time'])
        else:
            raise hdfError("ERROR!! \'time\' or \'t\' array is not found not in {}".format(item))

    def get_timestep(self):
        timeline = self.get_time()
        return timeline[1] - timeline[0]

    def get_names(self, tcf, gname):
        items = list(self['/'].values())
        names = items[0][tcf][gname]['names'][()]
        return names

    def get_atoms(self, tcf, gname):
        items = list(self['/'].values())
        atoms = items[0][tcf][gname]['atoms'][()]
        return atoms

    def get_smarts(self, tcf, gname):
        items = list(self['/'].values())
        smarts = items[0][tcf][gname]['smarts'][()]
        return smarts

    def get_trjCount(self):
        return len(self.get_trjList())

    def get_groupList(self, tcf='', traj_name=''):
        wrong_names = []
        if traj_name and tcf:
            groups = list(self['/'][traj_name][tcf].keys())

            for gname in groups:
                if not isinstance(self['/'][traj_name][tcf][gname], (str, Group)):
                    wrong_names.append(gname)
        elif tcf:
            items = list(self['/'].values())
            groups = list(items[0][tcf].keys())

            for gname in groups:
                if not isinstance(items[0][tcf][gname], (str, Group)):
                    wrong_names.append(gname)

        else:
            groups = set(self.get_groupList('acf'))
            groups.update(self.get_groupList('ccf'))
            groups = list(groups)

        for w_el in wrong_names:
            groups.remove(w_el)
        return sorted(groups)

    def get_trjList(self):
        return self['/'].keys()

    def get_tcfList(self):
        return self._get_zeroTrj().keys()

    def get_groupSize(self, tcf, gname):
        cgroup = self._get_zeroGroup(tcf, gname)
        if cgroup is not None:
            return cgroup['group_size'][()]

    # def get_TrjInfo(self):
    #     pass

    def _get_zeroGroup(self, tcf, gname):
        trj = self._get_zeroTrj()
        if gname in trj[tcf].keys():
            return trj[tcf][gname]

        raise hdfError("ERROR!! {} not in {}".format(gname, tcf))

    def _get_zeroTrj(self):
        return list(self['/'].values())[0]

    def get_tcf_shape(self, tcf, gname):
        g = self._get_zeroGroup(tcf, gname)
        return g['cf'].shape

    ### is have

    def has_group(self, tcf, gname):
        trj = self._get_zeroTrj()
        return gname in trj[tcf].keys()

    def has_tcf(self, tcf):
        trj = self._get_zeroTrj()
        return tcf in trj.keys()

    ### Checkers

    def cmp_t(self):
        arr = self.get_time()
        for item in self.tcf_iter():
            if not np.array_equal(arr, item['t']):
                print("ERROR!! time arrays are not equal!")
                return False
        return True

    def cmp_groups(self):
        try:
            for tcf in ['acf', 'ccf']:
                groups = self.get_groupList(tcf)
                for key, item in self.trj_iter():
                    glist = self.get_groupList(tcf, key)
                    if not groups == glist:
                        print("ERROR!! group names are not equal")
                for gname in groups:
                    # get atoms, cf, gs, names, smarts
                    g = self._get_zeroGroup(tcf, gname)
                    if not isinstance(g, (str, Group)):
                        continue
                    atoms = g['atoms'][()]
                    cf = g['cf']
                    gs = g['group_size']
                    names = g['names'][()]
                    smarts = g['smarts'][()]
                    for group in self.group_iter(tcf, gname):
                        if atoms != group['atoms'][()]:
                            raise hdfError("ERROR!! atoms are not equal")
                        if cf.shape != group['cf'].shape:
                            raise hdfError("ERROR!! cf are not equal")
                        if gs != group['group_size']:
                            raise hdfError("ERROR!! group size are not equal")
                        if names != group['names'][()]:
                            raise hdfError("ERROR!! names are not equal")
                        if smarts != group['smarts'][()]:
                            raise hdfError("ERROR!! smarts are not equal")
                return True
        except hdfError as e:
            print(e, file=sys.stderr)
            return False
        except Exception as e:
            raise e

    def check_file(self):
        if self.cmp_t() and self.cmp_groups():
            return True
        else:
            return False

    ### Manipulation

    def array_tcf(self, tcf, gname):
        g = self._get_zeroGroup(tcf, gname)
        trjCount = self.get_trjCount()
        arr = np.zeros((trjCount, *g['cf'].shape))
        for i, group in zip(range(trjCount), self.group_iter(tcf, gname, True)):
            arr[i] = group['cf']
        return arr

    def mean_tcf(self, tcf='', gname=''):
        g = self._get_zeroGroup(tcf, gname)
        mean = np.zeros(g['cf'].shape)
        partial_sum_squares = np.zeros(g['cf'].shape)
        trjCount = self.get_trjCount()
        if tcf and gname:
            arr = self.array_tcf(tcf, gname)
        return np.mean(arr, axis=0), np.std(arr, axis=0, ddof=1) / np.sqrt(trjCount - 1)

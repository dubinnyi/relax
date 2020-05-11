#!/usr/bin/python3 -u

import h5py

import numpy as np

from argparse import ArgumentParser


# not used
newTauC = 2974.0


# #########################
# DEFINITIONS
# #########################


PS = 10**(-12)

# vacuum permeability in N * A ** (-2) (SI)
MU_o = 1.2566370614359 * 10 ** (-6)

# Planck's constant in J * s (SI)
h = 6.6260689633 * 10 ** (-34)

# exact Larmor frequency of nucleus
# The values for 800 MHz NMR
omega = {'C' :  2 * np.pi * 201.2058454 * 10**6,
         'N' : -2 * np.pi * 81.0596495  * 10**6,
         'H' :  2 * np.pi * 799.8737876 * 10**6}

# gyromagnetic ratio of C**13, N**15, H**1
gamma = {'C':  6.7262 * 10**7,
         'N': -2.71157145117 * 10**7,
         'H':  2.67522209970 * 10**8}

# chemical shift anisotropy of C**13 (CSA), delta_sigma=25.0* 10**(-6) for methine group, defi'ne' systematic error: 2*sigma=26.0 * 10**(-6)
# 2)chemical shift anisotropy of N**15 in an amide group in betta-sheet: -162+-6 ppm, overall uncertainty +-9 ppm, see Yao, Grishaev, Cornilescu, Bax 2009
delta_sigma = {'C':  25.0  * 10**(-6),
               'N': -170.0 * 10**(-6)}

# uncertainty for the length of CH, NH or HH vector
drXH = {'C': 0.007 * 10**(-10),
        'N': 0.005 * 10**(-10),
        'H': 0.01  * 10**(-10)}

# uncertainty for CSA
ddelta_sigma = {'C':  13.0 * 10**(-6),
                'N': -9.0  * 10**(-6)}

# Effective length of the vector X1X2 including bond stretching only ! Note, r(CH)=1.109 !!!
rRef = {'CH': 1.109 * 10**(-10),
        'CC': 1.526 * 10**(-10),
        'CN': 1.329 * 10**(-10),
        'HH': 1.76  * 10**(-10),
        'NH': 1.025 * 10**(-10)}

# relative combined uncertainty of d00
def d00(ctype, ntype, r):
    return (1/20) * (MU_o/(4*np.pi))**2 * (h/(2*np.pi))**2 * gamma[ctype]**2 * gamma[ntype]**2 * r**(-6)

def dd00(ctype, ntype, r):
    return (1/20) * (MU_o/(4*np.pi))**2 * (h/(2*np.pi))**2 * gamma[ctype]**2 * gamma[ntype]**2 * 6 * r**(-7) * drXH[ctype]

# CSA
def c00(ntype):
    return (1/15) * (delta_sigma[ntype])**2

# relative combined uncertainty of c00
def dc00(ntype):
    return (1/15) * 2 * delta_sigma[ntype] * ddelta_sigma[ntype]

# d00[X, "H", rRef["CH"]
# dd00[X, "H", rRef["CH"]
# d00[X, "C", rRef["CC"]
# dd00[X, "C", rRef["CC"]


def tau(t1, t2):
    return (t1 * t2) / (t1 + t2)


#####
# Непонятно что. Надо спросить
#####
def vec(j):
    return corFunList[j][4:5]

# ###############################
# Data Prepare
# ###############################

# Gaussian distribution of parameters generated from a fit and its covariance matrix. dd is the sample volume
def distrib(dd, covar):
    rng = np.random.default_rng()
    return rng.multinomial(dd, covar)

def rules(i, m):
    return []

# ###############
# Formulas
# ###############

# distribution of J-functions J(w). newTauC is overall correlation time for rotational diffusion of a protein molecule
def J(w, A, tauJ):
    #return  2 * ordPar * newTauC * PS / (1 + (w * newTauC * PS)**2) +\
    # Order parameter is the first amplitude A[0]
    # tauc is the first time tauJ[0]
    # Other times are exponential fits corrected for tauc
    return np.sum(2 * A * tauJ * PS / (1 + (w * tauJ * PS) ** 2))

# Distribution of R1 calculated from J-functions
def R1(X, H, A, tauJ):
    bond_type = X + H
    return d00(X, H, rRef[bond_type]) * \
           (3 * J(omega[X],            A, tauJ) +
                J(omega[H] - omega[X], A, tauJ) +
            6 * J(omega[H] + omega[X], A, tauJ)) + \
           c00(X) * omega[X] ** 2 * J(omega[X], A, tauJ)

# Distribution for a part of NOE
def toNOE(X, H, A, tauJ):
    bond_type = X + H
    return (gamma[H] / gamma[X]) * \
           (d00(X, H, rRef[bond_type]) *
            (6 * J(omega[H] + omega[X], A, tauJ) - \
             J(omega[H] - omega[X], A, tauJ)))


def prepare_A_and_tauJ(params, tauc):
    # Pre-exponential factors from fit procedure
    listA = params[0:-1:2]
    nexps = listA.shape[0]

    # The first amplitude A[0] is the order parameter
    # Following amplitudes are pre-exponentials from fit procedure
    A = np.zeros(nexps+1)
    A[0] = params[-1] # order parameter
    A[1:] = listA

    # The result of nonlinear least squares fitting in molecular frame
    tauFit = params[1::2]

    # The first time tauJ[0] is tauc -- overall isotropic rotation time
    # Other times are fitted times corrected for tauc
    tauJ = np.zeros(nexps+1)
    tauJ[0] = tauc
    # Apply tauc to all fitted times tauFit
    # Times are corrected for overall isotropic rotation with time tauc
    # That times are ready to be used in J(omega) -- spectral density functions
    tauJ[1:] = tau(tauFit, tauc)

    return A, tauJ

def calcRelaxDistrib(dd, tauc, params, covar):
    # All relaxation-active parts of a single relaxation group. numParts=1 for an NH-group
    numParts = 1
    nr = 1
    rGroup = 'NH'
    X = 'N'
    H = 'H'
    for i in range(numParts):
        #j = relGroups[nr][i]
        #print(corFunList[j])
        # vec(j)
        #distrib(dd, covar)
        for m in range(1, dd + 1):
            A, tauJ = prepare_A_and_tauJ(params, tauc)
            # A[0] is order parameter
            # tauJ[0] is tauc
            r1 = R1(X, H, A, tauJ)
            print(r1)


def load_data(filename, group, tcf, nexp):
    with h5py.File(filename, 'r') as fd:
        hdf_group = fd[group]
        if 'names' in hdf_group:
            hdf_names = hdf_group['names'][()]
            names = hdf_names.splitlines()
        else:
            names=''
        hdf_exp = hdf_group['exp{}'.format(nexp)]
        params = hdf_exp['params'][::]
        covar  = hdf_exp['covar'][::]
        return params, covar, names

def main(args):
    params, covar, names = load_data(args.filename, args.group, args.tcf, args.nexp)

    dd=1
    for i in range(params.shape[0]):
        print("Calculate relaxation for {}".format(names[i]))
        calcRelaxDistrib(dd, args.tauc, params[i], covar[i])



if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument('-i', default=0, type=int, help='index in data array for calculation')
    #parser.add_argument('-s', '--exp-start', default=4, type=int, help='Number of exponents to start from')
    #parser.add_argument('-f', '--exp-finish', default=6, type=int, help='Number of exponents when finish')
    parser.add_argument('--nexp', default=5, type=int, help='Number of exps to use')
    parser.add_argument('-g', '--group', default='NH', help='Which group you want to calculate')
    parser.add_argument('--tcf', default='acf', help='Need to fit data from hdf')
    parser.add_argument('--tauc', type=float, help='TauC of the molecule in picoseconds')
    parser.add_argument('-o', '--output', default='out.hdf', help='filename for saving results')
    args = parser.parse_args()
    main(args)

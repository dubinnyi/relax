import fitter.fitter as f
import numpy as np

from argparse import ArgumentParser
from fitter.exp_model import CModel

parser = ArgumentParser()
parser.add_argument("-p", "--pairs", type=str, help="File with atom pairs definition")
parser.add_argument("-f", "--func", type=str, help="File with acf or ccf")


# [time, func, err^2]

def main():
    options = parser.parse_args()
    fd = open(options.func, 'r')
    data = fd.read().split('\n\n')
    meanData = []
    for arr in data:
        with open('tmp.csv', 'w') as tmpfd:
                tmpfd.write(arr)
        meanData.append(np.loadtxt('tmp.csv', delimiter=','))

    for arr in meanData:
        fitModel = f.Fitter(arr[:, 1], arr[:, 2], arr[:, 0])
        for nexp in range(2, 6):
            fitModel.fmodel = CModel(nexp)
            fitModel.fitting()

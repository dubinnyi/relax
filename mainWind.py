#!/usr/bin/env python3

import os
import sys
import h5py

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidget

from PyQt5.QtGui import QColor

#Graph
import numpy as np

from gui.mplCanvas import DynamicMplCanvas
# from gui.listGUI import ListGUI
from view import Ui_MainWindow
from setWind import settingsWind
from hdf5_API import hdfAPI

colors = {'SELECTED':'#7fc97f', 'USUAL':'#ffffff'}

class App(QMainWindow, Ui_MainWindow):
    def __init__(self):
        self.fdData = None
        self.fdPair = None
        self.data = Data()
        self.plot = []
        # self.settings = setWind()

        super().__init__()
        self.setupUi(self)

        self.mplcanvas=DynamicMplCanvas()
        l = QtWidgets.QVBoxLayout(self.Graph)
        l.addWidget(self.mplcanvas)

        #### Buttons
        self.Prev.clicked.connect(self.getPrev)
        self.Next.clicked.connect(self.getNext)
        self.plotButton.clicked.connect(self.plotData)

        #### ListWidget
        self.PairList.clear()
        self.PairList.itemDoubleClicked.connect(self.listwidget2clicked)

        #### MenuBar

        # .npy
        self.actionAdd_data.triggered.connect(self.browseFileData)
        self.actionAdd_pairs.triggered.connect(self.browseFilePair)

        # .csv
        self.actionAdd_data_in_csv.triggered.connect(self.browseDataCSV)

        # .hdf5
        self.actionLoad_from_hdf5.triggered.connect(self.browseFileHDF5)

#### Navigation
    def getPrev(self):
        self.data.getPrev()
        self.plotData()

    def getNext(self):
        self.data.getNext()
        self.plotData()

    def setText(self, text):
        self.title.setText(text)

    def openSetWind(self, fname=None):
        self.setWind = settingsWind(self.fdData)
        if self.setWind.start():
            pass
        else:
            self.fdData.close()

    # def loadFileData(self):
    #     self.data.addData(np.load(self.fdData))

#### Browsing Files
    def _getFile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file',
         '/home/incredible/Diplom/data/',"(*)")
        return fname[0]

    def loadFilePairs(self):
        pairs = self.fdPair.readlines()
        pairs = list(map(lambda x: x.rstrip(), pairs))
        self.data.setPairs(pairs)
        for pair in pairs:
            self.PairList.addItem(pair)

    def browseFileData(self):
        self.data.cleanData()
        with open(self._getFile(), 'rb') as fd:
            self.fdData_t = np.load(fd)
            self.fdData = np.load(fd)
            self.data.setTime(self.fdData_t)
            self.data.setData(self.fdData)

    # def browseFileData(self):
    #     self.data.cleanData()
    #     self.fdData = np.load(self._getFile())
    #     self.data.setTime(self.fdData[0])
    #     self.data.setData(self.fdData[1:])

    def browseFilePair(self):
        self.data.cleanPairs()
        self.PairList.clear()
        self.fdPair = open(self._getFile(), 'r')
        self.loadFilePairs()

    # def browseTimelineCSV(self):
    #     self.data.setTime(np.loadtxt(self._getFile(), delimiter=','))

    def browseDataCSV(self):
        fname = self._getFile()
        data = np.loadtxt(fname, delimiter=',')
        pair = os.path.basename(fname)
        time = data[:, 0]
        func = data[:, 1]
        err  = data[:, 2]
        self.data.setTime(time)
        self.data.addData(func)
        self.data.addPair(pair)
        self.PairList.addItem(pair)
        self.data.addError(err)

    def browseFileHDF5(self):
        self.fdData = hdfAPI(self._getFile(), 'r')
        self.openSetWind()
        # self.loadFileData()

#### Plotting
    def _plot(self):
        self.mplcanvas.draw_fig()

    def plotData(self):
        self.mplcanvas.clear()
        if self.plot:
            self.plotList()
        else:
            x, y = self.data.getX(), self.data.getY()
            self.mplcanvas.update_figure(x, y)
            self.plotErrors(x, y)
            self._plot()
            self.setText(self.data.getPair())

    def plotList(self):
        for plotty in self.plot:
            x, y = self.data.getX(), self.data.getY(plotty)
            self.mplcanvas.update_figure(x, y, plotty)
            self.plotErrors(x, y, plotty)
        self.mplcanvas.draw_fig()

    def plotErrors(self, x, y, label=None):
        if self.data.hasErrors():
            errs = self.data.getErrors(label)
            self.mplcanvas.add_Yerrors(x, y, errs)

##### ListWidget
    def listwidget2clicked(self, item):
        if self.isPlot(item.text()):
            self.rmPlot(item.text())
            item.setBackground(QColor(colors['USUAL']))
        else:
            self.addPlot(item.text())
            item.setBackground(QColor(colors['SELECTED']))

## Plot some in one
    def addPlot(self, label):
        self.plot.append(label)

    def rmPlot(self, label):
        self.plot.pop(self.plot.index(label))

    def isPlot(self, label):
        return label in self.plot

class Data:
    def __init__(self):
        self.cid = 0
        self.count = 0
        self.pairs = []
        self.data = []
        self.errors = []
        self.time = 0
        self.plot = []

    def setTime(self, time):
        self.time = time

    def setData(self, data):
        self.data = data
        self.count = data.shape[0]

    def addData(self, data):
        self.data.append(data)
        self.count += 1

    def setPairs(self, pairs):
        self.pairs = pairs

    def addPair(self, pair):
        self.pairs.append(pair)

    def setErrors(self, errs):
        self.errors = errs

    def addError(self, err):
        self.errors.append(err)

    def getNext(self):
        if self.cid + 1 < self.count:
            self.cid += 1

    def getPrev(self):
        if self.cid > 0:
            self.cid -= 1

    def getX(self):
        return self.time

    def getY(self, label=None):
        if label is not None:
            return self.data[self.pairs.index(label)]
        else:
            return self.data[self.cid]

    def getPair(self):
        return self.pairs[self.cid]

    def getErrors(self, label=None):
        if label is not None:
            return self.errors[self.pairs.index(label)]
        else:
            return self.errors[self.cid]

    def cleanPairs(self):
        self.pairs = []

    def cleanData(self):
        self.data = []

    def cleanErrors(self):
        self.errors = []

    def clearAll(self):
        self.cleanData()
        self.cleanPairs()
        self.cleanErrors()

    def findPair(self, label):
        self.cid = self.pairs.index(label)

    def hasErrors(self):
        return self.errors

def main():
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
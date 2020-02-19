#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os.path as op

#PyQt stuff
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow#, QWidget
from PyQt5.QtCore import pyqtSlot
from PyQt5 import uic

#Graph
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

curdir=op.dirname(op.abspath(__file__))


class DynamicMplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure()
        self.axes = fig.add_subplot(111)
        super(DynamicMplCanvas, self).__init__(fig)

        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.x, self.y=[],[]

    def update_figure(self, x ,y):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        self.x, self.y=x ,y
        self.axes.cla()
        self.axes.plot(self.x, self.y, 'r')
        self.draw()


class GraphWindow(QMainWindow):
    def __init__(self):
        super(GraphWindow, self).__init__()
        uic.loadUi(op.join(curdir, "graph.ui"), self)

        self.mplcanvas=DynamicMplCanvas()
        l = QtWidgets.QVBoxLayout(self.Graph)
        l.addWidget(self.mplcanvas)

        #fig = Figure(figsize=(width, height), dpi=dpi)
        self.on_PlotButton_clicked()



    @pyqtSlot()
    def on_PlotButton_clicked(self):

        try:
            npts=int(self.NPLE.text())
            x1=float(self.X1LE.text())
            x2=float(self.X2LE.text())
            f=self.FUNCLE.text()
            x=np.linspace(x1, x2, npts)
            y=eval(f,{"np":np,"x":x})
            self.mplcanvas.update_figure(x, y)
            #print("CLICK!",npts,x1,x2,y)
        except Exception as e:
            #Message box!
            QtWidgets.QMessageBox.critical(self, 'Error!', str(e))
            pass
        #


def main():
    app = QApplication(sys.argv)
    w=GraphWindow()

#     w = QWidget()
#     w.resize(250, 150)
#     w.move(300, 300)
#     w.setWindowTitle('Simple')
    w.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


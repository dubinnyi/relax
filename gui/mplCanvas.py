import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5 import QtWidgets



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

    def update_figure(self, x ,y, label=' '):
        self.axes.plot(x, y, label=label)

    def add_Yerrors(self, x, y, errs):
        self.axes.errorbar(x, y, yerr=errs*10)

    def draw_fig(self):
        self.axes.legend()
        self.draw()

    def clear(self):
        self.axes.cla()

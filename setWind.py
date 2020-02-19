import os
import sys
import view

from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidget, QDialog

from ui.set_view import Ui_setWind

colors = {'SELECTED':'#7fc97f', 'USUAL':'#ffffff'}

class settingsWind(QDialog, Ui_setWind):
    """docstring for setWind"""
    def __init__(self, fd):
        self.fd = fd
        self.trjselect = []
        self.tcfselect = []
        self.gselect = []

        super().__init__()
        self.setupUi(self)

        #### TrajList
        self.TrajList.clear()
        self.add_trjItems()
        self.TrajList.itemDoubleClicked.connect(self.traj2click)

        #### TcfList
        self.TcfList.clear()
        self.TcfList.itemDoubleClicked.connect(self.tcf2click)

        #### GroupList
        self.GroupList.clear()
        self.GroupList.itemDoubleClicked.connect(self.g2click)

        #### Button
        # self.OkButton.clicked.connect(self.okButton)
        self.ExtractButton.clicked.connect(self.extractButton)

    def start(self):
        return self.exec_()

    def addfd(self, fd):
        self.fd = fd
        print(self.fd)

    def add_trjItems(self):
        self.TrajList.addItems(self.fd.get_trjList())

    def add_tcfItems(self):
        self.TcfList.addItems(self.fd.get_tcfList())

    def add_gItems(self, tcf):
        self.GroupList.addItems(self.fd.get_tcfGroupList(tcf))

    def traj2click(self, item):
        if self.isTrj(item.text()):
            self.rmTrj(item.text())
            item.setBackground(QColor(colors['USUAL']))
        else:
            self.addTrj(item.text())
            item.setBackground(QColor(colors['SELECTED']))

    def addTrj(self, label):
        self.trjselect.append(label)
        if len(self.trjselect) == 1:
            self.add_tcfItems()

    def rmTrj(self, label):
        self.trjselect.pop(self.trjselect.index(label))

    def isTrj(self, label):
        return label in self.trjselect


    def tcf2click(self, item):
        if self.isTcf(item.text()):
            self.rmTcf(item.text())
            item.setBackground(QColor(colors['USUAL']))
        else:
            self.addTcf(item.text())
            item.setBackground(QColor(colors['SELECTED']))
            self.add_gItems(item.text()












































                )

    def addTcf(self, label):
        self.tcfselect.append(label)

    def rmTcf(self, label):
        self.tcfselect.pop(self.tcfselect.index(label))

    def isTcf(self, label):
        return label in self.tcfselect

    def g2click(self, item):
        if self.isGroup(item.text()):
            self.rmGroup(item.text())
            item.setBackground(QColor(colors['USUAL']))
        else:
            self.addGroup(item.text())
            item.setBackground(QColor(colors['SELECTED']))

    def addGroup(self, label):
        self.gselect.append(label)

    def rmGroup(self, label):
        self.gselect.pop(self.gselect.index(label))

    def isGroup(self, label):
        return label in self.gselect

    def okButton(self):
        pass

    def extractButton(self):
        pass
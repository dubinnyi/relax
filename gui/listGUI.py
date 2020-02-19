from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QListWidget


class ListGUI(QListWidget):
    def __init__(self):
        super(GUI, self).__init__()
        self.layout = QVBoxLayout()
        self.initGUI()

#    def getLayout(self):
#        return self.layout

    def initGUI(self, items):
#        self.listWidget = QListWidget()
        for item in items:
            self.addItem(QListWidgetItem(item))

        self.itemClicked.connect(self.listwidgetclicked)
        self.layout.addWidget(self)       #.listWidget)

    def listwidgetclicked(self, item):
        print('!!! click {}'.format(item.text()))
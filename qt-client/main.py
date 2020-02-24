from PySide2 import QtWidgets, QtCore, QtGui, QtNetwork
from ApiResultModel import ApiResultModel
from time import sleep
from Worker import Worker
from pathlib import Path
from MangaSiteFactory import MangaSiteEnum
from MainTableView import MainTableView
from functools import partial
from InfoLayout import InfoLayout


class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.df = []

        self.threadpool = QtCore.QThreadPool()

        self.textEdit = QtWidgets.QLineEdit(self)
        self.textEdit.setText('stone')        

        self.searchBtn = QtWidgets.QToolButton(self)
        self.searchBtn.setText('Search')
        self.info_layout = InfoLayout()
        self.resultTb = MainTableView(self)
        self.resultMdl = ApiResultModel(self.df, self)
        self.searchBtn.clicked.connect(self.resultTb.search_manga)
        self.textEdit.returnPressed.connect(self.resultTb.search_manga)
        self.mangaSiteComboBox = QtWidgets.QComboBox(self)
        for site in list(MangaSiteEnum):
            self.mangaSiteComboBox.addItem(site.value)
        self.mangaSiteComboBox.currentIndexChanged.connect(self.resultTb.set_site)

        self.resultTb.setModel(self.resultMdl)
        

        # Arrange layout
        OuterHBLayout = QtWidgets.QHBoxLayout(self)
        VBlayout1 = QtWidgets.QVBoxLayout()
        VBlayout2 = QtWidgets.QVBoxLayout()
        HBlayout = QtWidgets.QHBoxLayout()
        
        
        HBlayout.setAlignment(QtCore.Qt.AlignTop)
        HBlayout.addWidget(self.textEdit)
        HBlayout.addWidget(self.searchBtn)
        HBlayout.addWidget(self.mangaSiteComboBox)

        OuterHBLayout.addLayout(VBlayout2)
        OuterHBLayout.addLayout(VBlayout1)

        VBlayout1.addLayout(HBlayout)
        VBlayout1.addWidget(self.resultTb)
        VBlayout2.addLayout(self.info_layout)

        self.manager = QtNetwork.QNetworkAccessManager(self)
    

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setGeometry(QtCore.QRect(200, 200, 800, 600))
    window.show()
    sys.exit(app.exec_())

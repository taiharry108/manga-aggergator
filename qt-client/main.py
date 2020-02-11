from PySide2 import QtWidgets, QtCore, QtGui
from ApiResultModel import ApiResultModel, ApiResultModelStatus
import pandas as pd
from time import sleep
from Worker import Worker
from pathlib import Path
from MangaAggreController import MangaAggreController
from MainTableView import MainTableView
from functools import partial


DUMMY_DATA = pd.DataFrame([[1, 2, 3], [2, 4, 6]], columns=['a', 'b', 'c'])


class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.df = DUMMY_DATA

        self.threadpool = QtCore.QThreadPool()

        self.textEdit = QtWidgets.QLineEdit(self)
        self.textEdit.setText('stone')

        # self.textEdit.editingFinished.connect(self.test)
        self.searchBtn = QtWidgets.QToolButton(self)
        self.searchBtn.setText('Search')
        self.resultTb = MainTableView(self)
        self.resultMdl = ApiResultModel(DUMMY_DATA, self)
        self.searchBtn.clicked.connect(self.resultTb.search_manga)
        self.textEdit.returnPressed.connect(self.resultTb.search_manga)

        self.resultTb.setModel(self.resultMdl)
        self.resultTb.downloader.download_completed.connect(
            self.resultMdl.page_download_finished)

        # Arrange layout
        VBlayout = QtWidgets.QVBoxLayout(self)
        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.setAlignment(QtCore.Qt.AlignTop)
        HBlayout.addWidget(self.textEdit)
        HBlayout.addWidget(self.searchBtn)
        VBlayout.addLayout(HBlayout)
        VBlayout.addWidget(self.resultTb)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setGeometry(500, 300, 800, 600)
    window.show()
    sys.exit(app.exec_())

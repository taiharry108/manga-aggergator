from enum import Enum
from PySide2 import QtCore

Qt = QtCore.Qt


class ApiResultModelStatus(Enum):
    N = 0
    SEARCH = 1
    INDEX = 2
    CHAPTER = 3


class ApiResultModel(QtCore.QAbstractTableModel):

    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data
        self.page_downloaded = {}

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])

    def headerData(self, column, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[column]

    def setNewData(self, data):
        old_col_n = self._data.shape[1]
        self._data = data
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, old_col_n - 1)

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            self._data.iloc[row, column] = value
            self.dataChanged.emit(index, index, role)
            return True

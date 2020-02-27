from enum import Enum
from PySide2 import QtCore
from collections import defaultdict

Qt = QtCore.Qt


class ApiResultModelStatus(Enum):
    N = 0
    SEARCH = 1
    INDEX = 2
    CHAPTER = 3


class ApiResultModel(QtCore.QAbstractTableModel):
    def __init__(self, data: list, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data        
        
        self.page_downloaded = defaultdict(set)
        
    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                row_idx = index.row()
                column_idx = index.column()
                return_v = str(self._data[row_idx][self.headers[column_idx]])                
                return return_v

    def headerData(self, column, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.headers[column]

    def setNewData(self, data):
        old_col_n = len(self.headers)
        
        self._data = data
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, old_col_n - 1)

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            
            self._data[row][self.headers[column]] = value
            self.dataChanged.emit(index, index, [role])
            return True
    
    def page_download_finished(self, index):
        row = index.row()
        column1 = self.get_col_idx_from_name('Pages Downloaded')
        column3 = self.get_col_idx_from_name('Progress')

        total_pages_downloaded = int(self._data[row]['Pages Downloaded']) + 1
        self.setData(self.index(row, column1), total_pages_downloaded)
        progress = total_pages_downloaded / float(self._data[row]['Total Pages'])
        self.setData(self.index(row, column3), progress)
    
    def get_col_idx_from_name(self, name: str) -> int:
        if not name in self.headers:
            return -1
        else:
            return self.headers.index(name)

    def set_total_pages(self, index, total_pages):
        total_page_idx = self.get_col_idx_from_name('Total Pages')
        self.setData(self.index(index.row(), total_page_idx), total_pages)
    
    def get_data_for_row(self, row_idx: int, col_name: str):
        return self._data[row_idx][col_name]
    
    def get_status(self):
        return self.parent().currentStatus
    
    def get_headers(self):
        if self.status == ApiResultModelStatus.INDEX:
            return ['name', 'm_type', 'title', 'Progress', 'Pages Downloaded', 'Total Pages', 'Download']
        elif self.status == ApiResultModelStatus.SEARCH:
            return ['name']
        else:
            return []
            # return ["Test"]

    headers = property(get_headers)
    status = property(get_status)

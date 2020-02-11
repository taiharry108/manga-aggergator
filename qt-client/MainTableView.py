from PySide2 import QtWidgets, QtCore, QtGui
from ApiResultModel import ApiResultModel, ApiResultModelStatus
import pandas as pd
from Worker import Worker
from pathlib import Path
from MangaAggreController import MangaAggreController
from functools import partial
from ProgressBarDelegate import ProgressBarDelegate
from Downloader import Downloader

DUMMY_DATA = pd.DataFrame([[1, 2, 3], [2, 4, 6]], columns=['a', 'b', 'c'])



class MainTableView(QtWidgets.QTableView):
    def new_table_return(self, output):
        output, new_status = output
        df = pd.DataFrame(output)
        self.df = df
        self.model().setNewData(df)
        self.currentStatus = new_status
        if new_status == ApiResultModelStatus.INDEX:
            df['Progress'] = 0
            df['Pages Downloaded'] = 0
            df['Total Pages'] = 0
            self.setItemDelegateForColumn(
                df.columns.tolist().index('Progress'), ProgressBarDelegate())

    def search_manga(self):
        keyword = self.parent().textEdit.text()
        worker = Worker(self.ctr.searchManga, keyword=keyword,
                        new_status=ApiResultModelStatus.SEARCH)
        worker.signals.result.connect(self.new_table_return)
        self.threadpool.start(worker)

    def get_chapters(self, url):
        worker = Worker(self.ctr.getChapters, url=url,
                        new_status=ApiResultModelStatus.INDEX)
        worker.signals.result.connect(self.new_table_return)
        self.threadpool.start(worker)

    def get_pages(self, url, index):
        worker = Worker(self.ctr.getPages, url=url,
                        new_status=ApiResultModelStatus.INDEX)
        worker.signals.result.connect(partial(self.downloader.download, index))
        worker.signals.result.connect(partial(self.set_total_pages, index))

        self.threadpool.start(worker)
    
    def set_total_pages(self, index, output):
        output, _ = output
        self.model().set_total_pages(index, len(output))
    
    def tableDoubleClicked(self, index):
        row = index.row()
        model = self.model()
        if not 'url' in self.df.columns.tolist():
            return
        url_col = self.df.columns.tolist().index('url')
        url = model.data(model.index(row, url_col))

        if self.currentStatus == ApiResultModelStatus.SEARCH:
            self.get_chapters(url)
        elif self.currentStatus == ApiResultModelStatus.INDEX:
            self.get_pages(url, index)

    def __init__(self, parent=None):
        super(MainTableView, self).__init__(parent)
        self.root_path = Path('./downloads')
        self.df = pd.DataFrame()
        self.currentStatus = ApiResultModelStatus.N

        self.threadpool = QtCore.QThreadPool()
        self.doubleClicked.connect(self.tableDoubleClicked)
        self.ctr = MangaAggreController()
        self.downloader = Downloader(self, self.root_path, ctr=self.ctr)
        


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainTableView()
    window.setGeometry(500, 300, 800, 600)
    window.show()
    sys.exit(app.exec_())

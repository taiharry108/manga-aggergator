from PySide2 import QtWidgets, QtCore, QtGui
from ApiResultModel import ApiResultModel, ApiResultModelStatus
import pandas as pd
from Worker import Worker
from pathlib import Path
from MangaAggreController import MangaAggreController
from functools import partial
from ProgressBarDelegate import ProgressBarDelegate
import numpy as np, os
from collections import defaultdict
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

    # def page_download_finished(self, dl_key):
    #     self.page_downloaded_dict[dl_key] += 1
    #     total_page = self.total_page_dict[dl_key]
    #     if self.page_downloaded_dict[dl_key] + 1 == total_page:
    #         self.page_idx_dict.pop(dl_key)
    #         self.page_downloaded_dict.pop(dl_key)
    #         self.total_page_dict.pop(dl_key)
    #         self.timer_dict.pop(dl_key)

    #         zip_fn = f'{dl_key.as_posix()}.zip'
    #         zip_path = dl_key.as_posix()

    #         zipdir(zip_fn, zip_path)


    # def start_download_work(self, pages, index, dl_key):
    #     page_idx = self.page_idx_dict[dl_key]
    #     if page_idx == len(pages):
    #         self.timer_dict[dl_key].stop()
    #         return
    #     output_dir, url = pages[page_idx]
    #     fn = output_dir/f'{page_idx}'
    #     worker = Worker(self.ctr.downloadPage, filename=fn,
    #                     url=url)
    #     self.page_idx_dict[dl_key] += 1
    #     self.threadpool.start(worker)
    #     worker.signals.finished.connect(partial(self.model(
    #     ).page_download_finished, index))
    #     worker.signals.finished.connect(partial(self.page_download_finished, dl_key))

        

    # def download_pages(self, index, output):
    #     output, new_status = output
    #     self.currentStatus = new_status

    #     pages_to_download = []
    #     model = self.model()
    #     total_page_idx = self.df.columns.tolist().index('Total Pages')
    #     model.setData(model.index(index.row(), total_page_idx), len(output))

    #     for page_d in output:
    #         name = page_d['name']
    #         title = page_d['title']
    #         page = page_d['page']
    #         url = page_d['url']

    #         output_dir = self.root_path/name/title
    #         output_dir.mkdir(parents=True, exist_ok=True)
    #         pages_to_download.append((output_dir, url))
        
    #     dl_key = output_dir

    #     self.timer_dict[dl_key] = timer = QtCore.QTimer()
    #     self.total_page_dict[dl_key] = len(output)
    #     self.page_idx_dict[dl_key] = 0
    #     timer.setInterval(50)
    #     timer.timeout.connect(
    #         partial(self.start_download_work, pages_to_download, index, dl_key=dl_key))

    #     timer.start()

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

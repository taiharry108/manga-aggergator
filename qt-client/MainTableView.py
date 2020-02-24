from PySide2 import QtWidgets, QtCore, QtGui
from ApiResultModel import ApiResultModel, ApiResultModelStatus
import pandas as pd
from Worker import Worker
from pathlib import Path
from functools import partial
from ProgressBarDelegate import ProgressBarDelegate
from Downloader import Downloader
from MangaSiteFactory import get_manga_site, MangaSiteEnum
from typing import List
from Manga import Manga


class MainTableView(QtWidgets.QTableView):
    def new_table_return(self, output):
        output, new_status = output
        df = pd.DataFrame(output)
        print(df, new_status)
        self.df = df
        self.model().setNewData(df)
        self.currentStatus = new_status
        if new_status == ApiResultModelStatus.INDEX and len(df) != 0:
            df['Progress'] = 0
            df['Pages Downloaded'] = 0
            df['Total Pages'] = 0
            self.setItemDelegateForColumn(
                df.columns.tolist().index('Progress'), ProgressBarDelegate())

    def search_manga(self):
        keyword = self.parent().textEdit.text()
        self.site.search_manga(keyword)

    def get_chapters(self, url):
        self.site.get_index_page(url)

    def get_pages(self, url, index: QtCore.QModelIndex):
        row = index.row()
        m_type = self.df.iloc[row]['m_type']
        chapter_idx = self.df.iloc[row]['chapter_idx']
        self.site.download_chapter(self.manga, m_type, chapter_idx)
    
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
    
    def search_result_return(self, mangas: List[Manga]):
        output = ([{"name": manga.name, 'url':manga.url} for manga in mangas], ApiResultModelStatus.SEARCH)
        self.new_table_return(output)
    
    def index_page_return(self, manga: Manga):        
        chapter_dict = manga.get_chapters()
        output = []
        name = manga.name
        for key, chapters in chapter_dict.items():
            m_type = key
            for chapter_idx, chapter in enumerate(chapters):
                title = chapter.title
                url = chapter.page_url
                output.append({'name': name, 'url': url, 'title':title, 'm_type': m_type, 'chapter_idx': chapter_idx})
        output = (output, ApiResultModelStatus.INDEX)
        self.manga = manga
        self.new_table_return(output)
    
    def set_site(self, idx):
        self.site = get_manga_site(list(MangaSiteEnum)[idx], self.downloader)
        self.site.search_result.connect(self.search_result_return)
        self.site.index_page.connect(self.index_page_return)

    def __init__(self, parent=None):
        super(MainTableView, self).__init__(parent)
        self.root_path = Path('./downloads')
        self.df = pd.DataFrame()
        self.currentStatus = ApiResultModelStatus.N

        self.threadpool = QtCore.QThreadPool()
        self.doubleClicked.connect(self.tableDoubleClicked)
        self.downloader = Downloader(self, self.root_path)
        self.manga = None
        self.set_site(0)
        


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainTableView()
    window.setGeometry(500, 300, 800, 600)
    window.show()
    sys.exit(app.exec_())

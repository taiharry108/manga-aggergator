from PySide2 import QtWidgets, QtCore
from ApiResultModel import ApiResultModel, ApiResultModelStatus
from pathlib import Path
from functools import partial
from ProgressBarDelegate import ProgressBarDelegate
from Downloader import Downloader
from MangaSiteFactory import get_manga_site, MangaSiteEnum
from typing import List
from Manga import Manga, MangaIndexTypeEnum
import zipfile, os
import shutil

def zipdir(fn, path):
    with zipfile.ZipFile(fn, 'w', zipfile.ZIP_DEFLATED) as ziph:
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))


class MainTableView(QtWidgets.QTableView):
    def new_table_return(self, output):
        output, new_status = output
        df = output
        self.df = df
        model = self.model()
        model.setNewData(df)
        self.currentStatus = new_status
        if new_status == ApiResultModelStatus.INDEX and len(df) != 0:
            for d in df:
                d['Progress'] = 0
                d['Pages Downloaded'] = 0
                d['Total Pages'] = 0
            self.setItemDelegateForColumn(
                model.get_col_idx_from_name('Progress'), ProgressBarDelegate())

    def search_manga(self):
        keyword = self.parent().textEdit.text()
        self.site.search_manga(keyword)

    def get_chapters(self, url):
        self.site.get_index_page(url)

    def get_pages(self, url, index: QtCore.QModelIndex):
        row = index.row()
        m_type = self.df[row]['m_type']
        chapter_idx = self.df[row]['chapter_idx']
        self.site.download_chapter(self.manga, m_type, chapter_idx)
        self.index_dict[(m_type, chapter_idx)] = index
    
    
    def tableDoubleClicked(self, index):
        row = index.row()
        model = self.model()
        if len(self.df) == 0:
            return
        if not 'url' in self.df[0].keys():
            return
        url_col = model.get_col_idx_from_name('url')
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
    
    def init_sites(self):
        self.sites = [get_manga_site(manga_site_enum, self.downloader) for manga_site_enum in list(MangaSiteEnum)]
        for site in self.sites:
            site.search_result.connect(self.search_result_return)
            site.index_page.connect(self.index_page_return)
            site.index_page.connect(self.parent().info_layout.update_info)
            site.get_pages_completed.connect(self.get_pages_return)        
    
    def set_site(self, idx):
        self.site = self.sites[idx]
    
    def get_pages_return(self, pages: list, manga: Manga, m_type: MangaIndexTypeEnum, idx: int):
        index = self.index_dict[(m_type, idx)]
        self.model().set_total_pages(index, len(pages))

    
    def image_download_complete(self, manga: Manga, m_type: MangaIndexTypeEnum, idx: int, page_idx: int):
        index = self.index_dict[(m_type, idx)]
        self.model().page_download_finished(index)
    
    def chapter_download_complete(self, manga: Manga, m_type: MangaIndexTypeEnum, idx: int):
        self.index_dict.pop((m_type, idx))
        output_dir = self.downloader.get_output_dir(manga, m_type, idx)
        zip_path = output_dir.as_posix()
        zip_fn = output_dir.with_suffix('.zip')
        zipdir(zip_fn, zip_path)
        shutil.rmtree(zip_path)

    
    def __init__(self, parent=None):
        super(MainTableView, self).__init__(parent)
        self.root_path = Path('./downloads')
        self.df = []
        self.currentStatus = ApiResultModelStatus.N

        self.threadpool = QtCore.QThreadPool()
        self.doubleClicked.connect(self.tableDoubleClicked)
        self.downloader = Downloader(self, self.root_path)
        self.downloader.download_complete.connect(self.image_download_complete)
        self.downloader.chapter_download_complete.connect(self.chapter_download_complete)
        self.manga = None
        self.init_sites()
        self.set_site(0)
        self.index_dict = {}
        


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainTableView()
    window.setGeometry(500, 300, 800, 600)
    window.show()
    sys.exit(app.exec_())

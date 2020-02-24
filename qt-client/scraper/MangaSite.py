from typing import List
from Manga import Manga, MangaIndexTypeEnum
from Downloader import Downloader
from PySide2 import QtCore
Signal = QtCore.Signal
class MangaSite(QtCore.QObject):
    search_result = Signal(list)
    index_page = Signal(Manga)
    get_pages_completed = Signal(list, object, object, int)
    def __init__(self, name, url, *args, **kwargs):
        super(MangaSite, self).__init__(*args, **kwargs)
        self._name = name
        self._url = url
        self._downloader = Downloader()
        self._manga_dict = {}
    
    def get_manga(self, manga_name, manga_url=None) -> Manga:
        if not manga_name in self._manga_dict.keys():
            assert manga_url is not None
            self._manga_dict[manga_name] = Manga(name=manga_name, url=manga_url, site=self)
        return self._manga_dict[manga_name]

    def get_name(self):
        return self._name

    def get_url(self):
        return self._url
        
    def get_downloader(self) -> Downloader:
        return self._downloader
    
    def search_manga(self, keyword: str) -> List[Manga]:
        raise NotImplementedError

    def get_index_page(self, page):
        raise NotImplementedError

    def get_page_urls(self, manga, m_type, idx):
        raise NotImplementedError
    
    name = property(get_name)
    url = property(get_url)
    downloader = property(get_downloader)

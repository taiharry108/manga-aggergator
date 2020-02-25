from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MangaSite import MangaSite

class MangaIndexTypeEnum(Enum):
    CHAPTER = "Chapter"
    VOLUME = "Volume"
    MISC = "Misc"

class Chapter(object):
    def __init__(self, title: str, page_url: str):
        self._title = title
        self._page_url = page_url

    def get_title(self):
        return self._title
        
    def get_page_url(self):
        return self._page_url
        
    
    title = property(get_title)
    page_url = property(get_page_url)


class Manga(object):
    def __init__(self, name: str, url: str, site: "MangaSite"):
        self._name = name
        self._url = url
        self._chapters = {key: [] for key in list(MangaIndexTypeEnum)}
        self._site = site
        self._last_update = None
        self._finished = None
    
    def add_chapter(self, m_type: MangaIndexTypeEnum, title:str, page_url:str):
        self._chapters[m_type].append(Chapter(title, page_url))

    def get_name(self) -> str:
        return self._name

    def get_url(self) -> str:
        return self._url
    
    def get_site(self):
        return self._site

    def get_chapter(self, m_type: MangaIndexTypeEnum, idx: int) -> Chapter:
        return self._chapters[m_type][idx]

    def get_chapters(self):
        return self._chapters
    
    def get_finished(self):
        return self._finished
    
    def get_last_update(self):
        return self._last_update
    
    def get_thum_img(self):
        return self._thum_img
    
    def set_meta_data(self, meta_data):
        self._last_update = meta_data.get('last_update')
        self._finished = meta_data.get('finished')
        self._thum_img = meta_data.get('thum_img')

        
    name = property(get_name)
    url = property(get_url)
    site = property(get_site)
    chapters = property(get_chapters)
    last_udpate = property(get_last_update)
    finished = property(get_finished)
    thum_img = property(get_thum_img)

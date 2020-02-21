from enum import Enum

class MangaIndexTypeEnum(Enum):
    CHAPTER = 1
    VOLUME = 2
    MISC = 3

class Chapter(object):
    def __init__(self, manga, title, page_url):
        self._manga = manga
        self._title = title
        self._page_url = page_url

    def get_manga(self):
        return self._manga
        
    def get_title(self):
        return self._title
        
    def get_page_url(self):
        return self._page_url
        
    
    manga = property(get_manga)
    title = property(get_title)
    page_url = property(get_page_url)


class Manga(object):
    def __init__(self, name, url):
        self._name = name
        self._url = url
        self._chapters = {key: [] for key in list(MangaIndexTypeEnum)}
    
    def add_chapter(self, m_type: MangaIndexTypeEnum, title:str, page_url:str):
        self._chapters[m_type].append(Chapter(self, title, page_url))

    def get_name(self):
        return self._name

    def get_url(self):
        return self._url

    def get_chapters(self):
        return self._chapters

    
    name = property(get_name)
    url = property(get_url)
    chapters = property(get_chapters)

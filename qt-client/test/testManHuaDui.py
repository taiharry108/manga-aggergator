import unittest
from MangaSiteFactory import get_manga_site, MangaSiteEnum
from MangaSite import MangaSite
from Manga import Manga, Chapter, MangaIndexTypeEnum
from Downloader import Downloader
from PySide2 import QtWidgets, QtCore
from typing import List, Dict
from functools import partial


def call_timeout(loop):
    loop.quit()
    raise TimeoutError


class TestManHuaDui(unittest.TestCase):
    def test_init(self):
        mhd = get_manga_site(MangaSiteEnum.ManHuaDui, Downloader(None, './downloads'))
        self.assertEqual(mhd.name, '漫畫堆')
        self.assertEqual(mhd.url, 'https://www.manhuadui.com/')
    
    
    def test_seach_manga1(self):

        def search_callback(loop, result: List[Manga]):
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 4)
            foundFlag = False        
            for manga in result:
                if manga.name == '朋友游戏':
                    foundFlag = True
                    break
            self.assertTrue(foundFlag)
            self.assertEqual(manga.url, 'https://www.manhuadui.com/manhua/pengyouyouxi/')
            loop.quit()

        timeout = 5000
        if QtWidgets.QApplication.instance() is None:
            QtWidgets.QApplication([])

        loop = QtCore.QEventLoop()
        mhd = get_manga_site(MangaSiteEnum.ManHuaDui, Downloader(None, './downloads'))
        
        mhd.search_result.connect(partial(search_callback, loop))
        
        mhd.search_manga('pengyouyouxi')
        if timeout is not None:
            QtCore.QTimer.singleShot(timeout, partial(call_timeout, loop))
        loop.exec_()
        
    def test_get_index_page(self):
        def index_callback(loop, manga: Manga):
            chapters = manga.chapters
            self.assertIsInstance(chapters, dict)
            self.assertEqual(len(chapters), 3)
            self.assertEqual(len(chapters[MangaIndexTypeEnum.CHAPTER]), 75)
            chapter = chapters[MangaIndexTypeEnum.CHAPTER][39]
            self.assertEqual(chapter.title, '40话')
            loop.quit()
            
        timeout = 5000
        if QtWidgets.QApplication.instance() is None:
            QtWidgets.QApplication([])
        
        mhd = get_manga_site(MangaSiteEnum.ManHuaDui, Downloader(None, './downloads'))
        mhd.get_index_page('https://www.manhuadui.com/manhua/pengyouyouxi/')
        
        loop = QtCore.QEventLoop()
        mhd.index_page.connect(partial(index_callback, loop))

        if timeout is not None:
            QtCore.QTimer.singleShot(timeout, partial(call_timeout, loop))
        loop.exec_()

    def test_get_page_urls(self):
        def page_urls_callback(loop, page_urls, manga: Manga, m_type: MangaIndexTypeEnum, idx: int):
            self.assertEqual(len(page_urls), 40)
            self.assertEqual(page_urls[0], 'https://mhimg.eshanyao.com/ManHuaKu/p/pengyouyouxi/75/145829.jpg')
            self.assertEqual(page_urls[1], 'https://mhimg.eshanyao.com/ManHuaKu/p/pengyouyouxi/75/145830.jpg')
            self.assertEqual(page_urls[-3], 'https://mhimg.eshanyao.com/ManHuaKu/p/pengyouyouxi/75/145866.jpg')
            loop.quit()

        timeout = 10000
        if QtWidgets.QApplication.instance() is None:
            QtWidgets.QApplication([])
        
        mhd = get_manga_site(MangaSiteEnum.ManHuaDui, Downloader(None, './downloads'))
        manga = Manga(
            name='朋友游戏', url='https://www.manhuadui.com/manhua/pengyouyouxi/',
            site=mhd)
        manga.add_chapter(MangaIndexTypeEnum.CHAPTER, title='75话「还是老样子呢」',
                          page_url='https://www.manhuadui.com/manhua/pengyouyouxi/461357.html')

        mhd.get_page_urls(manga, MangaIndexTypeEnum.CHAPTER, 0)
        loop = QtCore.QEventLoop()

        mhd.get_pages_completed.connect(partial(page_urls_callback, loop))
        

        if timeout is not None:
            QtCore.QTimer.singleShot(timeout, partial(call_timeout, loop))
        loop.exec_()
    
    def test_get_manga(self):
        mhd = get_manga_site(MangaSiteEnum.ManHuaDui, Downloader(None, './downloads'))
        name = '朋友游戏'
        url = 'https://www.manhuadui.com/manhua/pengyouyouxi/'
        manga = mhd.get_manga(name, url)
        self.assertEqual(manga.name, name)
        self.assertEqual(manga.url, url)
        with self.assertRaises(AssertionError):
            mhd.get_manga('Test')

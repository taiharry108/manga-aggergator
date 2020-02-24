import unittest
import MangaSiteFactory
from MangaSite import MangaSite
from Manga import Manga, Chapter, MangaIndexTypeEnum
from Downloader import Downloader
from PySide2 import QtWidgets, QtCore
from typing import List, Dict
from functools import partial

DLR = Downloader(None)

def call_timeout(loop):
    loop.quit()
    raise TimeoutError


class TestManHuaGui(unittest.TestCase):
    def test_init(self):
        mhg = MangaSiteFactory.get_manga_site(MangaSiteFactory.MangaSiteEnum.ManHuaGui)
        self.assertEqual(mhg.name, '漫畫鬼')
        self.assertEqual(mhg.url, 'https://www.manhuagui.com/')
    
    
    def test_seach_manga(self):

        def search_callback(loop, result: List[Manga]):
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)
            foundFlag = False        
            for manga in result:
                if manga.name == '火影忍者':
                    foundFlag = True
                    break
            self.assertTrue(foundFlag)
            self.assertEqual(
                manga.url, 'https://www.manhuagui.com/comic/4681/')
            loop.quit()

        timeout = 5000
        if QtWidgets.QApplication.instance() is None:
            QtWidgets.QApplication([])

        loop = QtCore.QEventLoop()
        mhg = MangaSiteFactory.get_manga_site(MangaSiteFactory.MangaSiteEnum.ManHuaGui)
        
        mhg.search_result.connect(partial(search_callback, loop))
        
        self.assertEqual(DLR, mhg.downloader)
        mhg.search_manga('naruto')
        if timeout is not None:
            QtCore.QTimer.singleShot(timeout, partial(call_timeout, loop))
        loop.exec_()
        
    def test_get_index_page(self):
        def index_callback(loop, manga: Manga):
            chapters = manga.chapters
            self.assertIsInstance(chapters, dict)
            self.assertEqual(len(chapters), 3)
            self.assertEqual(len(chapters[MangaIndexTypeEnum.CHAPTER]), 10)
            chapter = chapters[MangaIndexTypeEnum.VOLUME][-1]
            self.assertEqual(chapter.title, '第72卷')
            loop.quit()
            
        timeout = 5000
        if QtWidgets.QApplication.instance() is None:
            QtWidgets.QApplication([])
        
        mhg = MangaSiteFactory.get_manga_site(MangaSiteFactory.MangaSiteEnum.ManHuaGui)
        mhg.get_index_page('https://www.manhuagui.com/comic/4681/')
        
        loop = QtCore.QEventLoop()
        mhg.index_page.connect(partial(index_callback, loop))

        if timeout is not None:
            QtCore.QTimer.singleShot(timeout, partial(call_timeout, loop))
        loop.exec_()
    
    def test_get_index_page2(self):
        def index_callback(loop, manga: Manga):
            chapters = manga.chapters
            self.assertIsInstance(chapters, dict)
            self.assertEqual(len(chapters), 3)
            self.assertEqual(len(chapters[MangaIndexTypeEnum.CHAPTER]), 195)
            chapter = chapters[MangaIndexTypeEnum.CHAPTER][156]
            self.assertEqual(chapter.title, '第157话 归还之魂')
            loop.quit()

        timeout = 5000
        if QtWidgets.QApplication.instance() is None:
            QtWidgets.QApplication([])

        mhg = MangaSiteFactory.get_manga_site(
            MangaSiteFactory.MangaSiteEnum.ManHuaGui)
        mhg.get_index_page('https://www.manhuagui.com/comic/19430/')

        loop = QtCore.QEventLoop()
        mhg.index_page.connect(partial(index_callback, loop))

        if timeout is not None:
            QtCore.QTimer.singleShot(timeout, partial(call_timeout, loop))
        loop.exec_()
    
    def test_get_page_urls(self):
        def page_urls_callback(loop, page_urls, manga: Manga, m_type: MangaIndexTypeEnum, idx: int):
            self.assertEqual(len(page_urls), 208)
            self.assertEqual(
                page_urls[0], 'https://i.hamreus.com/ps1/h/naruto/69/NARUTO69_000.jpg.webp?cid=194193&md5=9rdIwhvMsyOQN8DK0alICQ')
            self.assertEqual(
                page_urls[1], 'https://i.hamreus.com/ps1/h/naruto/69/NARUTO69_001b.png.webp?cid=194193&md5=9rdIwhvMsyOQN8DK0alICQ')
            self.assertEqual(
                page_urls[-2], 'https://i.hamreus.com/ps1/h/naruto/69/NARUTO69_104.png.webp?cid=194193&md5=9rdIwhvMsyOQN8DK0alICQ')
            loop.quit()

        timeout = 10000
        if QtWidgets.QApplication.instance() is None:
            QtWidgets.QApplication([])

        mhg = MangaSiteFactory.get_manga_site(MangaSiteFactory.MangaSiteEnum.ManHuaGui)
        manga = Manga(
            name='火影忍者', url='https://www.manhuagui.com/comic/4681/',
            site=mhg)
        manga.add_chapter(MangaIndexTypeEnum.CHAPTER, title='第69卷',
                          page_url='https://www.manhuagui.com/comic/4681/194193.html')
        mhg.get_page_urls(manga, MangaIndexTypeEnum.CHAPTER, 0)
        loop = QtCore.QEventLoop()

        mhg.get_pages_completed.connect(partial(page_urls_callback, loop))


        if timeout is not None:
            QtCore.QTimer.singleShot(timeout, partial(call_timeout, loop))
        loop.exec_()

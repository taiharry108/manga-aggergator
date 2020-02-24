# from Downloader import Downloader
# from PySide2 import QtWidgets, QtCore
# import unittest
# from Manga import Manga, MangaIndexTypeEnum
# from functools import partial
# from MangaSiteFactory import MangaSiteEnum, get_manga_site


# def call_timeout(loop):
#     loop.quit()    
#     raise TimeoutError


# class TestDownloader(unittest.TestCase):
#     # def test_download_image(self):
#     #     def page_download_complete(loop, manga: Manga, m_type: MangaIndexTypeEnum, idx: int):
#     #         with open(f'./downloads/{output_fn}.jpg', 'rb') as img_f:
#     #             data = img_f.read()

#     #         with open(f'./test/test_img01.jpg', 'rb') as test_img_f:
#     #             test_data = test_img_f.read()
#     #         self.assertEqual(data, test_data)

#     #         loop.quit()
#     #     timeout = 5000
#     #     if QtWidgets.QApplication.instance() is None:
#     #         QtWidgets.QApplication([])

#     #     d = Downloader(parent=None, root_path='./downloads')

#     #     loop = QtCore.QEventLoop()

#     #     url = 'https://img01.eshanyao.com/images/comic/234/466012/1582220514w0XhhEUQDv3hIGHM.jpg'
#     #     referer = 'https://www.manhuadui.com/manhua/guimiezhiren/466012.html'


#     #     d.download_image(url=url, output_fn='0', referer=referer)
#     #     d.download_complete.connect(partial(page_download_complete, loop))
#     #     QtCore.QTimer.singleShot(timeout, partial(call_timeout, loop))
#     #     loop.exec_()

#     def test_download_manga_chapter(self):
#         def chapter_download_complete(manga: Manga, m_type: MangaIndexTypeEnum, idx: int):
#             chapter = manga.get_chapter(m_type, idx)
#             print('completed', chapter.title)
            
         
#         timeout = 25000
#         if QtWidgets.QApplication.instance() is None:
#             QtWidgets.QApplication([])

#         d = Downloader(parent=None, root_path='./downloads')
#         loop = QtCore.QEventLoop()

#         manga = Manga(
#             name='鬼灭之刃', url='https://www.manhuadui.com/manhua/guimiezhiren/',
#             site=get_manga_site(MangaSiteEnum.ManHuaDui, d))
#         manga.add_chapter(MangaIndexTypeEnum.CHAPTER, title='195话 瞬息万变',
#                           page_url='https://www.manhuadui.com/manhua/guimiezhiren/466012.html')
#         manga.add_chapter(MangaIndexTypeEnum.CHAPTER, title='194话 灼热的伤痕',
#                           page_url='https://www.manhuadui.com/manhua/guimiezhiren/463850.html')
#         manga.add_chapter(MangaIndexTypeEnum.CHAPTER, title='193话 困难之门开启',
#                           page_url='https://www.manhuadui.com/manhua/guimiezhiren/460933.html')
#         m_type = MangaIndexTypeEnum.CHAPTER
#         for idx in [0]:
#             d.download_manga_chapter(manga, m_type, idx)
#         d.chapter_download_complete.connect(chapter_download_complete)
#         QtCore.QTimer.singleShot(timeout, partial(call_timeout, loop))

#         loop.exec_()

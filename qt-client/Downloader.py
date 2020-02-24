from PySide2 import QtCore, QtNetwork
from functools import partial
from pathlib import Path
from Manga import Manga, MangaIndexTypeEnum
import mimetypes
from collections import defaultdict
from typing import Callable

QNetworkReply = QtNetwork.QNetworkReply

class SingletonDecorator:
    def __init__(self, klass):
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance == None:
            self.instance = self.klass(*args, **kwargs)
        return self.instance

class _Downloader(QtCore.QObject):
    download_complete = QtCore.Signal(object, object, int, int)
    chapter_download_complete = QtCore.Signal(object, object, int)
    def __init__(self, parent, root_path: str='./downloads', *args, **kwargs):
        super(_Downloader, self).__init__(parent, *args, **kwargs)
        self.manager = QtNetwork.QNetworkAccessManager(parent)
        self.root_path = Path(root_path)
        self.timer_dict = defaultdict(QtCore.QTimer)
        self.page_downloaded_dict = defaultdict(int)
        self.page_idx_dict = defaultdict(int)
        self.total_page_dict = {}
        self.called_download_manga_chapter = False
    
    def get_request(self, url: str, callback: Callable[[QNetworkReply, dict], None], referer: str=None, meta_dict=None):
        req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        req.setHeader(QtNetwork.QNetworkRequest.UserAgentHeader,
                      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36')

        req.setAttribute(
            QtNetwork.QNetworkRequest.FollowRedirectsAttribute, True)
        if referer is not None:
            req.setRawHeader(bytes('Referer', 'utf-8'),
                             bytes(referer, 'utf-8'))
        reply = self.manager.get(req)
        reply.finished.connect(partial(callback, reply, meta_dict))
    
    def _save_img(self, reply: QNetworkReply, meta_dict: dict):
        output_fn = meta_dict['output_fn']

        status_code = reply.attribute(
            QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)

        if status_code == 200:
            content_type = reply.header(
                QtNetwork.QNetworkRequest.ContentTypeHeader)
            if content_type.startswith('image/webp'):
                extension = '.webp'
            else:
                extension = mimetypes.guess_extension(content_type)
            with open(self.root_path/f'{output_fn}{extension}', 'wb') as f:
                s = reply.readAll()
                f.write(s.data())
            self.emit_download_complete_signal(
                manga=meta_dict['manga'],
                m_type=meta_dict['m_type'],
                idx=meta_dict['idx'],
                page_idx=meta_dict['page_idx']
            )
            reply.deleteLater()
        
    def emit_chapter_download_complete(self, manga: Manga, m_type: MangaIndexTypeEnum, idx: int):
        self.chapter_download_complete.emit(manga, m_type, idx)
        output_dir = self.get_output_dir(manga, m_type, idx).as_posix()
        self.timer_dict.pop(output_dir)
        self.page_downloaded_dict.pop(output_dir)
        self.page_idx_dict.pop(output_dir)
        self.total_page_dict.pop(output_dir)
    
    def emit_download_complete_signal(self, manga: Manga, m_type: MangaIndexTypeEnum, idx: int, page_idx: int):        
        self.download_complete.emit(manga, m_type, idx, page_idx)
        output_dir = self.get_output_dir(manga, m_type, idx)
        dl_key = output_dir.as_posix()
        self.page_downloaded_dict[dl_key] += 1
        if self.page_downloaded_dict[dl_key] == self.total_page_dict[dl_key]:
            self.emit_chapter_download_complete(manga, m_type, idx)
    
    def download_image(self, url: str, output_fn: str, page_idx: int, manga: Manga, m_type: MangaIndexTypeEnum, idx: int):
        meta_dict = {
            'output_fn':output_fn,
            'manga': manga,
            'm_type': m_type,
            'idx': idx,
            'page_idx': page_idx}
        
        referer = manga.get_chapter(m_type, idx).page_url
        
        self.get_request(url, callback=self._save_img, referer=referer, meta_dict=meta_dict)
    
    def _download_images(self, pages: list, manga: Manga, m_type: MangaIndexTypeEnum, idx: int):
        output_dir = self.get_output_dir(manga, m_type, idx)
        dl_key = output_dir.as_posix()
        page_idx = self.page_idx_dict[dl_key]
        if page_idx == len(pages):
            self.timer_dict[dl_key].stop()
        else:
            url = pages[page_idx]
            fn = output_dir/f'{page_idx}'
            self.download_image(url=url, output_fn=fn.as_posix(), page_idx=page_idx, manga=manga, m_type=m_type, idx=idx)
            self.page_idx_dict[dl_key] += 1
    
    def get_output_dir(self, manga: Manga, m_type: MangaIndexTypeEnum, idx: int) -> Path:
        chapter = manga.get_chapter(m_type, idx)

        name = manga.name
        site = manga.site
        title = chapter.title

        output_dir = Path(site.name)/name/title
        return output_dir
    
    def download_pages(self, pages: list, manga: Manga, m_type: MangaIndexTypeEnum, idx: int):
        output_dir = self.get_output_dir(manga, m_type, idx)
        dl_key = output_dir.as_posix()
        timer = self.timer_dict[dl_key]
        self.total_page_dict[dl_key] = len(pages)

        timer.setInterval(50)
        
        timer.timeout.connect(
            partial(self._download_images, pages, manga, m_type, idx))

        timer.start()
    
    
    def download_manga_chapter(self, manga: Manga, m_type: MangaIndexTypeEnum, idx: int):
        site = manga.site
        output_dir = self.get_output_dir(manga, m_type, idx)
        (self.root_path/output_dir).mkdir(parents=True, exist_ok=True)
        
        
        site.get_page_urls(manga, m_type, idx)
        if not self.called_download_manga_chapter:
            self.called_download_manga_chapter = True
            site.get_pages_completed.connect(self.download_pages)
        


Downloader = SingletonDecorator(_Downloader)

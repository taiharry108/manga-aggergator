from PySide2 import QtCore, QtNetwork
from functools import partial
from pathlib import Path
from Manga import Manga, MangaIndexTypeEnum

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
    download_complete = QtCore.Signal(str)
    def __init__(self, parent, root_path: str='./downloads', *args, **kwargs):
        super(_Downloader, self).__init__(parent, *args, **kwargs)
        self.manager = QtNetwork.QNetworkAccessManager(parent)
        self.root_path = Path(root_path)
    
    def get_request(self, url: str, callback, referer: str=None, meta_dict=None):
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
                output_fn)
            reply.deleteLater()
    
    def emit_download_complete_signal(self, output_fn: str):
        self.download_complete.emit(str)

    def download_image(self, url: str, output_fn: str, referer: str=None):
        self.get_request(url, callback=self._save_img, referer=referer, meta_dict={'output_fn':output_fn})
    
    def download_manga_chapter(self, manga: Manga, m_type: MangaIndexTypeEnum, idx: int):
        chapter = manga.get_chapter(m_type, idx)

        name = manga.name
        site = manga.site
        page_url = chapter.page_url
        title = chapter.title

        site.get_page_urls(page_url)
        


Downloader = SingletonDecorator(_Downloader)

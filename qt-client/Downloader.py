from PySide2 import QtWidgets, QtCore, QtGui, QtNetwork
from functools import partial
from collections import defaultdict
from Worker import Worker
import zipfile
import os
import shutil
from pathlib import Path
import mimetypes

Signal = QtCore.Signal


def zipdir(fn, path):
    with zipfile.ZipFile(fn, 'w', zipfile.ZIP_DEFLATED) as ziph:
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))


class Downloader(QtCore.QObject):

    download_completed = Signal(object)

    def page_download_finished(self, dl_key, page_idx):
        self.page_downloaded_dict[dl_key] += 1
        total_page = self.total_page_dict[dl_key]
        if self.page_downloaded_dict[dl_key] == total_page:
            self.page_idx_dict.pop(dl_key)
            self.page_downloaded_dict.pop(dl_key)
            self.total_page_dict.pop(dl_key)
            self.timer_dict.pop(dl_key)
            self.index_dict.pop(dl_key)

            zip_fn = f'{dl_key.as_posix()}.zip'
            zip_path = dl_key.as_posix()

            zipdir(zip_fn, zip_path)
            shutil.rmtree(zip_path)

    def emit_download_complete_signal(self, dl_key, page_idx):
        self.download_completed.emit(self.index_dict[dl_key])
        self.page_download_finished(dl_key, page_idx)

    def __init__(self, parent, root_path):
        super(Downloader, self).__init__(parent)
        self.root_path = root_path

        self.timer_dict = {}
        self.index_dict = {}
        self.page_idx_dict = defaultdict(int)
        self.page_downloaded_dict = defaultdict(int)
        self.total_page_dict = {}

        self.threadpool = QtCore.QThreadPool()
        self.manager = QtNetwork.QNetworkAccessManager(self)

        
    def replyFinished(self, meta_dict, reply):
        status_code = reply.attribute(
            QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
        
        output_dir = meta_dict["output_dir"]
        dl_key = meta_dict["dl_key"]
        filename = meta_dict["filename"]
        if status_code == 200:
            content_type = reply.header(
                QtNetwork.QNetworkRequest.ContentTypeHeader)
            if content_type.startswith('image/webp'):
                extension = '.webp'
            else:
                extension = mimetypes.guess_extension(content_type)
            with open(filename.with_suffix(extension), 'wb') as f:
                s = reply.readAll()
                f.write(s.data())
            self.emit_download_complete_signal(output_dir, self.page_idx_dict[dl_key])
            reply.deleteLater()
    
    def downloadPage(self, output_dir, dl_key, filename: Path, url: str, referer=None):
        req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        req.setHeader(QtNetwork.QNetworkRequest.UserAgentHeader,
                      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36')
        
        req.setAttribute(QtNetwork.QNetworkRequest.FollowRedirectsAttribute, True)
        if referer is not None:
            req.setRawHeader(bytes('Referer', 'utf-8'), bytes(referer, 'utf-8'))
            req.setRawHeader(bytes('Test', 'utf-8'),
                             bytes('this is a test', 'utf-8'))
        meta_dict = {
            "output_dir": output_dir,
            "dl_key": dl_key,
            "filename": filename,
        }
        reply = self.manager.get(req)
        reply.finished.connect(partial(self.replyFinished, meta_dict, reply))
    

    def start_download_work(self, pages, dl_key, referer):
        page_idx = self.page_idx_dict[dl_key]
        if page_idx == len(pages):
            self.timer_dict[dl_key].stop()
        else:
            output_dir, url = pages[page_idx]
            fn = output_dir/f'{page_idx}'
            self.downloadPage(output_dir, dl_key, filename=fn,
                              url=url, referer=referer)
            self.page_idx_dict[dl_key] += 1

    def download(self, index, referer, output):
        download_instrc, _ = output
        pages_to_download = []

        for page_d in download_instrc:
            name = page_d['name']
            title = page_d['title']
            page = page_d['page']
            url = page_d['url']

            output_dir = self.root_path/name/title
            output_dir.mkdir(parents=True, exist_ok=True)
            pages_to_download.append((output_dir, url))

        dl_key = output_dir

        self.timer_dict[dl_key] = timer = QtCore.QTimer()
        self.index_dict[dl_key] = index
        self.total_page_dict[dl_key] = len(download_instrc)
        timer.setInterval(50)
        timer.timeout.connect(
            partial(self.start_download_work, pages_to_download, dl_key=dl_key, referer=referer))

        timer.start()

from PySide2 import QtWidgets, QtCore, QtGui
from functools import partial
from collections import defaultdict
from Worker import Worker
import zipfile
import os
import shutil

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

    def __init__(self, parent, root_path, ctr):
        super(Downloader, self).__init__(parent)
        self.root_path = root_path

        self.timer_dict = {}
        self.index_dict = {}
        self.page_idx_dict = defaultdict(int)
        self.page_downloaded_dict = defaultdict(int)
        self.total_page_dict = {}

        self.threadpool = QtCore.QThreadPool()
        self.ctr = ctr

    def start_download_work(self, pages, dl_key):
        page_idx = self.page_idx_dict[dl_key]
        if page_idx == len(pages):
            self.timer_dict[dl_key].stop()
        else:
            output_dir, url = pages[page_idx]
            fn = output_dir/f'{page_idx}'
            worker = Worker(self.ctr.downloadPage, filename=fn,
                            url=url)
            self.page_idx_dict[dl_key] += 1
            self.threadpool.start(worker)
            worker.signals.finished.connect(partial(
                self.emit_download_complete_signal, output_dir, self.page_idx_dict[dl_key]))

    def download(self, index, output):
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
            partial(self.start_download_work, pages_to_download, dl_key=dl_key))

        timer.start()

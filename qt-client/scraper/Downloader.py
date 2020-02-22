from PySide2 import QtCore, QtNetwork
from functools import partial

class SingletonDecorator:
    def __init__(self, klass):
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance == None:
            self.instance = self.klass(*args, **kwargs)
        return self.instance

class _Downloader(QtCore.QObject):
    def __init__(self, parent, *args, **kwargs):
        super(_Downloader, self).__init__(parent, *args, **kwargs)
        self.manager = QtNetwork.QNetworkAccessManager(parent)
    
    def get_request(self, url: str, callback, referer=None, meta_dict=None):
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


Downloader = SingletonDecorator(_Downloader)
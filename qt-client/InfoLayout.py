from PySide2 import QtWidgets, QtCore, QtGui, QtNetwork
from Manga import Manga
from Downloader import Downloader
class InfoLayout(QtWidgets.QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super(InfoLayout, self).__init__(*args, **kwargs)
        # self.setAlignment(QtCore.Qt.AlignHCenter)
        self.name_lbl = QtWidgets.QLabel('')
        # self.name_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.last_update_lbl = QtWidgets.QLabel('')
        self.finished_lbl = QtWidgets.QLabel('')
        self.img_lbl = QtWidgets.QLabel()
        self.img_lbl.setFixedSize(223, 300)
        self.addWidget(self.name_lbl)
        self.addWidget(self.img_lbl)
        self.addWidget(self.last_update_lbl)
        self.addWidget(self.finished_lbl)
        self.setAlignment(QtCore.Qt.AlignTop)        
    
    def set_thum_pic(self, reply: QtNetwork.QNetworkReply, meta_dict: dict):
        reader = QtGui.QImageReader(reply)
        pic = reader.read()
        pixmap = QtGui.QPixmap.fromImage(pic).scaledToHeight(300)
        self.img_lbl.setPixmap(pixmap)
        self.addWidget(self.img_lbl)
    
    def update_info(self, manga: Manga):
        self.downloader = Downloader(None, None)
        self.downloader.get_request(url=manga.thum_img, callback=self.set_thum_pic, referer=manga.url)
        manga_name = manga.name
        if manga.finished:
            self.finished_lbl.setText('完結')
        else:
            self.finished_lbl.setText('完結')
        
        self.last_update_lbl.setText(manga.last_udpate)
        self.name_lbl.setText(manga_name)
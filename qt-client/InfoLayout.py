from PySide2 import QtWidgets, QtCore, QtGui
class InfoLayout(QtWidgets.QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super(InfoLayout, self).__init__(*args, **kwargs)
        self.manga_name = "test"
        self.img = None
        self.name_lbl = QtWidgets.QLabel(self.manga_name)
        self.addWidget(self.name_lbl)
        self.setAlignment(QtCore.Qt.AlignTop)

        pixmap = QtGui.QPixmap('.')
        pixmap = pixmap.scaledToHeight(350)        
        label = QtWidgets.QLabel()
        label.setPixmap(pixmap)
        self.addWidget(label)
        

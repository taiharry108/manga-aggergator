from PySide2 import QtWidgets, QtCore, QtGui
import pandas as pd
from ApiResultModel import ApiResultModel

data = pd.DataFrame([("1", "Baharak", 10), ("2", "Darwaz", 20),
                     ("3", "Fays abad", 50), ("4", "Ishkashim", 30),
                     ("5", "Jurm", 60)], columns=['idx', 'name', 'progress'])
Slot = QtCore.Slot


class ProgressBarDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.isValid():
            fillPercent = float(index.data(0))
            # fillPercent = 0.3
            self.initStyleOption(option, index)
            painter.save()
            painter.setBrush(QtGui.QColor(0, 0, 200, 40))
            painter.setPen(QtCore.Qt.NoPen)

            right = QtCore.QSize(option.rect.width() *
                                 fillPercent, option.rect.height())
            painter.drawRect(QtCore.QRect(option.rect.topLeft(), right))
            painter.restore()

            option.backgroundBrush = QtGui.QBrush()
            widget = option.widget
            style = widget.style() if widget is not None else QtWidgets.QApplication.style()
            style.drawControl(QtWidgets.QStyle.CE_ItemViewItem,
                              option, painter, widget)


class ButtonDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.isValid():
            rect = option.rect
            btn = QtWidgets.QStyleOptionButton()
            btn.rect = QtCore.QRect(
                rect.left() + rect.width(), rect.top() + 1, rect.width(), rect.height() - 2)
            painter.fillRect(btn.rect, btn.palette.brush(
                QtGui.QPalette.Background))
            btn.text = "T1"
            widget = option.widget
            style = widget.style() if widget is not None else QtWidgets.QApplication.style()
            style.drawControl(QtWidgets.QStyle.CE_PushButton, btn, painter)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    tv = QtWidgets.QTableView()
    tv.setGeometry(QtCore.QRect(100, 100, 800, 600))

    model = ApiResultModel(data)

    def test():
        index = model.index(1, 2)
        value = int(model.data(index))
        model.setData(index, value + 1)

    tv.clicked.connect(test)
    tv.setModel(model)
    # tv.setItemDelegateForColumn(2, ProgressBarDelegate(parent=tv))
    tv.setItemDelegateForColumn(2, ButtonDelegate())
    tv.show()
    sys.exit(app.exec_())

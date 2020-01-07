from PySide2 import QtWidgets, QtCore, QtGui
import pandas as pd
from ApiResultModel import ApiResultModel

data = pd.DataFrame([("1", "Baharak", 10), ("2", "Darwaz", 60),
                     ("3", "Fays abad", 20), ("4", "Ishkashim", 80),
                     ("5", "Jurm", 100)], columns=['idx', 'name', 'progress'])

class ProgressBarDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.isValid():
            fillPercent = int(index.data(0)) / 100
            self.initStyleOption(option, index)
            painter.save()
            painter.setBrush(QtGui.QColor(0, 0, 200, 40))
            painter.setPen(QtCore.Qt.NoPen)
            
            right = QtCore.QSize((option.rect.width()) *
                                 fillPercent, option.rect.height())
            painter.drawRect(QtCore.QRect(option.rect.topLeft(), right))
            painter.restore()

            option.backgroundBrush = QtGui.QBrush()
            widget = option.widget
            style = widget.style() if widget is not None else  QtWidgets.QApplication.style()
            style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, option, painter, widget)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    tv = QtWidgets.QTableView()

    model = ApiResultModel(data)
    def test():
        index = model.index(1, 2)
        value = int(model.data(index))
        model.setData(index, value + 1)

    tv.clicked.connect(test)
    tv.setModel(model)
    tv.setItemDelegateForColumn(2, ProgressBarDelegate())
    tv.show()
    sys.exit(app.exec_())

from PySide2 import QtWidgets, QtCore, QtGui
from ApiResultModel import ApiResultModel


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

from PySide2 import QtWidgets, QtCore

class CheckBoxDelegate(QtWidgets.QStyledItemDelegate):
    """
    A delegate that places a fully functioning QCheckBox in every
    cell of the column to which it's applied
    """
    def getCheckBoxRect(self, option):
        check_box_style_option = QtWidgets.QStyleOptionButton()
        widget = option.widget
        style = widget.style() if widget is not None else QtWidgets.QApplication.style()        
        check_box_rect = style.subElementRect(QtWidgets.QStyle.SE_CheckBoxIndicator, check_box_style_option, None)
        check_box_point = QtCore.QPoint (option.rect.x() +
        option.rect.width() / 2 -
        check_box_rect.width() / 2,
        option.rect.y() +
        option.rect.height() / 2 -
        check_box_rect.height() / 2)
        return QtCore.QRect(check_box_point, check_box_rect.size())
    def createEditor(self, parent, option, index):
        '''        
        Important, otherwise an editor is created if the user clicks in this cell.
        ** Need to hook up a signal to the model
        '''
        return None

    def paint(self, painter, option, index):
        '''
        Paint a checkbox without the label.
        '''
        checked = index.model().data(index, QtCore.Qt.DisplayRole) == 'True'
        check_box_style_option = QtWidgets.QStyleOptionButton()
        
        # check_box_style_option.state |= QtWidgets.QStyle.State_Enabled

        # if (index.flags() & QtCore.Qt.ItemIsEditable) > 0:
        #     check_box_style_option.state |= QtWidgets.QStyle.State_Enabled
        # else:
        #     check_box_style_option.state |= QtWidgets.QStyle.State_ReadOnly

        if checked:
            check_box_style_option.state |= QtWidgets.QStyle.State_On
            check_box_style_option.state |= QtWidgets.QStyle.State_ReadOnly
        else:
            check_box_style_option.state |= QtWidgets.QStyle.State_Off
            check_box_style_option.state |= QtWidgets.QStyle.State_Enabled

        check_box_style_option.rect = self.getCheckBoxRect(option)

        # this will not run - hasFlag does not exist
        #if not index.model().hasFlag(index, QtCore.Qt.ItemIsEditable):
        #check_box_style_option.state |= QtWidgets.QStyle.State_ReadOnly

        # check_box_style_option.state |= QtWidgets.QStyle.State_Enabled

        widget = option.widget
        style = widget.style() if widget is not None else QtWidgets.QApplication.style()        
        style.drawControl(QtWidgets.QStyle.CE_CheckBox, check_box_style_option, painter)

    def editorEvent(self, event, model, option, index):
        '''
        Change the data in the model and the state of the checkbox
        if the user presses the left mousebutton or presses
        Key_Space or Key_Select and this cell is editable. Otherwise do nothing.
        '''
        # print('Check Box editor Event detected : ')        
        if event.type() == QtCore.QEvent.MouseButtonRelease or event.type() == QtCore.QEvent.MouseButtonDblClick:
            if event.button() != QtCore.Qt.LeftButton or not self.getCheckBoxRect(option).contains(event.pos()):
                return False
            else:
                model.setData(index, 'True')
                return True
        
        return False
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from pynput.keyboard import Key, Controller
import pyperclip

class MyTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super(MyTreeWidget, self).__init__(parent)
        self.itemSelectionChanged.connect(self.handle_item_selection)
        self.currentItemChanged.connect(self.handle_item_change)
        self.itemCollapsed.connect(self.itemCollapse)
        self.tooltip = QLabel(self)
        self.tooltip.setWindowFlags(Qt.ToolTip)
        self.timer = QTimer()
        self.keyboard = Controller()
        self.previous = None
        self.setUniformRowHeights(False)
    def setMainWindows(self, MainWindow):
        self.mw = MainWindow
    def setUi(self, Ui):
        self.ui = Ui
    #Строгий фокус
    def focusOutEvent(self, event):
        self.tooltip.hide()
        self.setFocus()
    #События кнопок
    def keyPressEvent(self, event):
        key = event.key()
        current_item = self.currentItem()
        parrent_item = current_item.parent()
        keys = [
            Qt.Key_1,
            Qt.Key_2,
            Qt.Key_3,
            Qt.Key_4,
            Qt.Key_5,
            Qt.Key_6,
            Qt.Key_7,
            Qt.Key_8,
            Qt.Key_9,
            Qt.Key_0,
            Qt.Key_Q,
            Qt.Key_W,
            Qt.Key_E,
            Qt.Key_R,
            Qt.Key_T,
            Qt.Key_Y,
            Qt.Key_U,
            Qt.Key_I,
            Qt.Key_O,
            Qt.Key_P,
        ]
        # Обработка нажатия цифр и символов для выбора элемента в дереве
        if key in keys:
            digit = keys.index(key) + 1
            if(parrent_item is not None and parrent_item.childCount() >= digit):
                self.setCurrentItem(current_item.parent().child(digit - 1))
            if(parrent_item is None and self.topLevelItemCount() >= digit):
                self.setCurrentItem(self.topLevelItem(digit - 1))
        else:
        # Обработка нажатия Enter для раскрытия элемента или вставки текста
            if key == Qt.Key_Return or key == Qt.Key_Enter:
                if (current_item is not None and current_item.childCount() > 0):
                    if current_item.isExpanded():
                        self.setCurrentItem(current_item.child(0))
                    else:
                        self.expandItem(current_item)
                else:
                    self.paste()
            else:
        # Обработка нажатия Backspace для возврата на уровень выше
                if key == Qt.Key_Backspace:
                    parent_item = current_item.parent()
                    if parent_item is not None:
                        self.setCurrentItem(parent_item)
                else:
                    self.handle_item_selection()
        self.handle_item_selection()
    #Событие двойного нажатия мышью
    def mouseDoubleClickEvent(self, e):
        current_item = self.currentItem()
        if (current_item is not None and current_item.childCount() > 0):
            if (not current_item.isExpanded()):
                self.expandItem(current_item)
            else:
                self.collapseItem(current_item)
        else:
            self.paste()
    # Событие сворачивания элемента
    def itemCollapse(self, item):
        self.setCurrentItem(item)
    #Действия при изменении выбранного элемента
    def handle_item_selection(self):
        current_item = self.currentItem()
        if current_item:
            self.numbering()
            data = current_item.data(0, Qt.UserRole)
            position = self.visualItemRect(current_item).topRight()
            window_position = self.mw.geometry().topLeft()
            tooltip_position =  position + window_position

            self.tooltip.hide()
            if(str(data) != ""):
                self.tooltip.setText(str(data))
                self.tooltip.move(tooltip_position)
                self.tooltip.show()
                #QTimer.singleShot(5000, self.tooltip.hide)
                # self.timer.setSingleShot(True)
                # self.timer.timeout.connect(self.tooltip.hide)
                # self.timer.start(5000)
    def handle_item_change(self, current, previous):
        self.previous = previous
    #Действие вставки текста
    def paste(self):
        current_item = self.currentItem()
        if (current_item is not None and current_item.childCount() == 0):
            data = current_item.data(0, Qt.UserRole)
            pyperclip.copy(str(data))
            self.tooltip.hide()
            self.mw.hide()
            self.key_press()
            if (self.ui.checkBox.isChecked()):
                QTimer.singleShot(1000, lambda: self.mw.close())
            else:
                QTimer.singleShot(200, lambda: self.mw.show())
    def key_press(self):
        with self.keyboard.pressed(Key.ctrl):
            self.keyboard.press('v')
            self.keyboard.release('v')
    def numbering(self):
        keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p']
        if (self.previous):
            if (self.currentItem().parent() != self.previous.parent()):
                if (self.currentItem().parent() is None):
                    count = len(keys) if self.topLevelItemCount() > len(keys) else self.topLevelItemCount()
                    for i in range(0, count):
                        self.topLevelItem(i).setText(1, keys[i])
                else:
                    count = len(keys) if self.currentItem().parent().childCount() > len(
                        keys) else self.currentItem().parent().childCount()
                    for i in range(0, count):
                        self.currentItem().parent().child(i).setText(1, keys[i])

                if (self.previous.parent() is None):
                    for i in range(0, self.topLevelItemCount()):
                        self.topLevelItem(i).setText(1, "")
                else:
                    for i in range(0, self.previous.parent().childCount()):
                        self.previous.parent().child(i).setText(1,"")
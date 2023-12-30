from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt

import TreeWidget_Class
from TreeWidget_Class import MyTreeWidget
import sqlite3
import os
import pyperclip, sys
from pynput.keyboard import Key, Controller
import PhraseEditor
import configparser

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 500)
        MainWindow.setStatusTip("")
        self.mw = MainWindow

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")

        self.config = configparser.ConfigParser()
        self.config.read(Ui_MainWindow.get_abspath("settings.ini"))

        self.treeWidget = Ui_MainWindow.create_tree_from_database(self, Ui_MainWindow.get_abspath(self.config["FastPaste"]["database_path"]), "Tree", )
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().setVisible(False)
        header = self.treeWidget.header()
        header.setStretchLastSection(False)  # Последний столбец больше не растягивается
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.treeWidget.setColumnWidth(1, 0)

        self.gridLayout.addWidget(self.treeWidget, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(4, 4, 4, 4)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setObjectName("checkBox")
        self.checkBox.setText("Закрыть")
        self.checkBox.setTristate(False)

        if(self.config["FastPaste"]["checkbox_close"] == "1"):
            self.checkBox.setCheckState(Qt.Checked)
        else:
            self.checkBox.setCheckState(Qt.Unchecked)

        self.checkBox.stateChanged.connect(self.on_state_changed)

        self.horizontalLayout.addWidget(self.checkBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Редактор записей")
        self.pushButton.clicked.connect(self.open_phrase_editor)

        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        QtCore.QCoreApplication.instance().aboutToQuit.connect(self.closeEvent)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "FastPaste"))
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.setSortingEnabled(__sortingEnabled)
    def create_tree_from_database(self, database_file, table_name):
        def build_tree(parent_item, parent_id):
            if parent_id in self.nodes:
                for row in self.nodes[parent_id]:
                    node_id, _, position, node_type, name, data = row
                    item = QtWidgets.QTreeWidgetItem(parent_item, [name])
                    item.setData(0, QtCore.Qt.UserRole, data)
                    item.setData(0, QtCore.Qt.UserRole + 1, node_type)
                    item.setTextAlignment(1, Qt.AlignRight)
                    if(node_type == 0):
                        item.setIcon(0, QtGui.QIcon(Ui_MainWindow.get_abspath('Images/folder.png')))
                    if (node_type == 2):
                        item.setIcon(0, QtGui.QIcon(Ui_MainWindow.get_abspath('Images/file.png')))

                    build_tree(item, node_id)

        if(os.path.isfile(database_file)):
            conn = sqlite3.connect(database_file)
            cursor = conn.cursor()

            # Получаем все записи из таблицы
            cursor.execute("SELECT * FROM " + table_name)
            rows = cursor.fetchall()

            # Создаем словарь, где ключом будет id узла, а значением будет список его дочерних узлов
            self.nodes = {}
            for row in rows:
                node_id, parent_id, position, node_type, name, data = row
                if parent_id in self.nodes:
                    self.nodes[parent_id].append(row)
                else:
                    self.nodes[parent_id] = [row]

            for parent_id in self.nodes:
                self.nodes[parent_id].sort(key=lambda x: x[2])  # сортируем по полю position

            tree = TreeWidget_Class.MyTreeWidget()
            tree.setMainWindows(self.mw)
            tree.setUi(self)
            tree.setColumnCount(2)  # Один столбец для имени узла
            # Строим дерево начиная с корневого узла (узлов с parent_id = 0)
            build_tree(tree, 0)

            keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p']
            count = len(keys) if tree.topLevelItemCount() > len(keys) else tree.topLevelItemCount()
            for i in range(count):
                tree.topLevelItem(i).setText(1, keys[i])

            conn.close()
            return tree

        else:
            mb = QtWidgets.QMessageBox()
            mb.setText("Не удалось найти БД")
            mb.setWindowTitle("Ошибка")
            mb.exec_()
            return TreeWidget_Class.MyTreeWidget()

        # Рекурсивная функция для построения дерева
    def get_abspath(name):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, name)
        return os.path.abspath(file_path)
    def open_phrase_editor(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = PhraseEditor.Ui_PhraseEditor()
        self.ui.setupUi(self.window)
        self.window.show()
        self.mw.close()
    def on_state_changed(self):
        if(self.checkBox.isChecked()):
            self.config["FastPaste"]["checkbox_close"] = str(1)
        else:
            self.config["FastPaste"]["checkbox_close"] = str(0)
    def closeEvent(self):
        with open("settings.ini",'w') as config:
            self.config.write(config)

# class MyTreeWidget(QTreeWidget):
#     def __init__(self, parent=None):
#         super(MyTreeWidget, self).__init__(parent)
#         self.itemSelectionChanged.connect(self.handle_item_selection)
#         self.currentItemChanged.connect(self.handle_item_change)
#         self.itemCollapsed.connect(self.itemCollapse)
#         self.tooltip = QLabel(self)
#         self.tooltip.setWindowFlags(Qt.ToolTip)
#         self.timer = QTimer()
#         self.keyboard = Controller()
#         self.previous = None
#         self.setUniformRowHeights(False)
#     #Строгий фокус
#     def focusOutEvent(self, event):
#         self.setFocus()
#     #События кнопок
#     def keyPressEvent(self, event):
#
#         key = event.key()
#         current_item = self.currentItem()
#         parrent_item = current_item.parent()
#
#         keys = [
#             Qt.Key_1,
#             Qt.Key_2,
#             Qt.Key_3,
#             Qt.Key_4,
#             Qt.Key_5,
#             Qt.Key_6,
#             Qt.Key_7,
#             Qt.Key_8,
#             Qt.Key_9,
#             Qt.Key_0,
#             Qt.Key_Q,
#             Qt.Key_W,
#             Qt.Key_E,
#             Qt.Key_R,
#             Qt.Key_T,
#             Qt.Key_Y,
#             Qt.Key_U,
#             Qt.Key_I,
#             Qt.Key_O,
#             Qt.Key_P,
#         ]
#         # Обработка нажатия цифр и символов для выбора элемента в дереве
#         if key in keys:
#             digit = keys.index(key) + 1
#             if(parrent_item is not None and parrent_item.childCount() >= digit):
#                 self.setCurrentItem(current_item.parent().child(digit - 1))
#             if(parrent_item is None and self.topLevelItemCount() >= digit):
#                 self.setCurrentItem(self.topLevelItem(digit - 1))
#         else:
#         # Обработка нажатия Enter для раскрытия элемента или вставки текста
#             if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
#                 if (current_item is not None and current_item.childCount() > 0):
#                     if current_item.isExpanded():
#                         self.setCurrentItem(current_item.child(0))
#                     else:
#                         self.expandItem(current_item)
#                 else:
#                     self.paste()
#             else:
#         # Обработка нажатия Backspace для возврата на уровень выше
#                 if key == QtCore.Qt.Key_Backspace:
#                     parent_item = current_item.parent()
#                     if parent_item is not None:
#                         self.setCurrentItem(parent_item)
#                 else:
#                     self.handle_item_selection()
#         self.handle_item_selection()
#     #Событие двойного нажатия мышью
#     def mouseDoubleClickEvent(self, e):
#         current_item = self.currentItem()
#         if (current_item is not None and current_item.childCount() > 0):
#             if (not current_item.isExpanded()):
#                 self.expandItem(current_item)
#             else:
#                 self.collapseItem(current_item)
#         else:
#             self.paste()
#     # Событие сворачивания элемента
#     def itemCollapse(self, item):
#         self.setCurrentItem(item)
#     #Действия при изменении выбранного элемента
#     def handle_item_selection(self):
#         current_item = self.currentItem()
#         if current_item:
#             self.numbering()
#             data = current_item.data(0, QtCore.Qt.UserRole)
#             position = ui.treeWidget.visualItemRect(current_item).topRight()
#             window_position = MainWindow.geometry().topLeft()
#             tooltip_position = window_position + position
#
#             self.tooltip.hide()
#             if(str(data) != ""):
#                 self.tooltip.setText(str(data))
#                 self.tooltip.move(tooltip_position)
#                 self.tooltip.show()
#                 self.timer.setSingleShot(True)
#                 self.timer.timeout.connect(self.tooltip.hide)
#                 self.timer.start(5000)
#     def handle_item_change(self, current, previous):
#         self.previous = previous
#     #Действие вставки текста
#     def paste(self):
#         current_item = self.currentItem()
#         if (current_item is not None and current_item.childCount() == 0):
#             data = current_item.data(0, QtCore.Qt.UserRole)
#
#             pyperclip.copy(str(data))
#             self.tooltip.hide()
#             MainWindow.hide()
#
#             self.key_press()
#
#
#             if (ui.checkBox.isChecked()):
#                 QTimer.singleShot(1000, lambda: app.quit())
#             else:
#                 QTimer.singleShot(200, lambda: MainWindow.show())
#
#     def key_press(self):
#         with self.keyboard.pressed(Key.ctrl):
#             self.keyboard.press('v')
#             self.keyboard.release('v')
#
#     def numbering(self):
#         keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p']
#         if (self.previous):
#             if (self.currentItem().parent() != self.previous.parent()):
#                 if (self.currentItem().parent() is None):
#                     count = len(keys) if self.topLevelItemCount() > len(keys) else self.topLevelItemCount()
#                     for i in range(0, count):
#                         self.topLevelItem(i).setText(1, keys[i])
#                 else:
#                     count = len(keys) if self.currentItem().parent().childCount() > len(
#                         keys) else self.currentItem().parent().childCount()
#                     for i in range(0, count):
#                         self.currentItem().parent().child(i).setText(1, keys[i])
#
#                 if (self.previous.parent() is None):
#                     for i in range(0, self.topLevelItemCount()):
#                         self.topLevelItem(i).setText(1, "")
#                 else:
#                     for i in range(0, self.previous.parent().childCount()):
#                         self.previous.parent().child(i).setText(1,"")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()  
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())



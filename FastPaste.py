from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
import sqlite3
import os
import pyperclip
from pynput.keyboard import Key, Controller
import time
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 500)
        MainWindow.setStatusTip("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.treeWidget = Ui_MainWindow.create_tree_from_database(self, Ui_MainWindow.get_abspath('Local.db'), "Tree")

        self.treeWidget.setGeometry(QtCore.QRect(0, 0, 400, 500))
        self.treeWidget.setObjectName("treeWidget")

        self.treeWidget.header().setVisible(False)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "FastPaste"))
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)

        self.treeWidget.setSortingEnabled(__sortingEnabled)

    def create_tree_from_database(self, database_file, table_name):
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()

        # Получаем все записи из таблицы
        cursor.execute("SELECT * FROM " + table_name)
        rows = cursor.fetchall()

        # Создаем словарь, где ключом будет id узла, а значением будет список его дочерних узлов
        nodes = {}
        for row in rows:
            node_id, parent_id, position, node_type, name, data = row
            if parent_id in nodes:
                nodes[parent_id].append(row)
            else:
                nodes[parent_id] = [row]

        for parent_id in nodes:
            nodes[parent_id].sort(key=lambda x: x[2])  # сортируем по полю position

        # Рекурсивная функция для построения дерева
        def build_tree(parent_item, parent_id):
            if parent_id in nodes:
                for row in nodes[parent_id]:
                    node_id, _, position, node_type, name, data = row
                    item = QtWidgets.QTreeWidgetItem(parent_item, [name])
                    item.setData(0, QtCore.Qt.UserRole, data)

                    if(node_type == 0):
                        item.setIcon(0, QtGui.QIcon(Ui_MainWindow.get_abspath('Images/folder.png')))
                    if (node_type == 2):
                        item.setIcon(0, QtGui.QIcon(Ui_MainWindow.get_abspath('Images/file.png')))

                    build_tree(item, node_id)

        tree = MyTreeWidget(self.centralwidget)
        tree.setColumnCount(1)  # Один столбец для имени узла

        # Строим дерево начиная с корневого узла (узлов с parent_id = 0)
        build_tree(tree, 0)

        #TODO Переопределить выделения

        # Закрываем соединение с базой данных
        conn.close()
        return tree

    def get_abspath(name):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, name)
        return os.path.abspath(file_path)

class MyTreeWidget(QtWidgets.QTreeWidget):
    #TODO Сделать нумерацию ветвей дерева для ориентации цифрами
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

        if key in keys:
            digit = keys.index(key) + 1
            if(parrent_item is not None and parrent_item.childCount() >= digit):
                self.setCurrentItem(current_item.parent().child(digit - 1))
            if(parrent_item is None and self.topLevelItemCount() >= digit):
                self.setCurrentItem(self.topLevelItem(digit - 1))

        # Обработка нажатия Enter для раскрытия элемента или вставки текста
        if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            if (current_item is not None and current_item.childCount() > 0):
                self.expandItem(current_item)
                self.setCurrentItem(current_item.child(0))
            if (current_item is not None and current_item.childCount() == 0):
                data = current_item.data(0, QtCore.Qt.UserRole)
                pyperclip.copy(str(data))
                MainWindow.hide()

                keyboard = Controller()

                with keyboard.pressed(Key.ctrl):
                    keyboard.press('v')
                    keyboard.release('v')
                #time.sleep(1)

                MainWindow.show()

        # Обработка нажатия Backspace для возврата на уровень выше
        if key == QtCore.Qt.Key_Backspace:
            parent_item = current_item.parent()
            if parent_item is not None:
                self.setCurrentItem(parent_item)

        # Обработка нажатия Up Down для перемещения по уровням
        if key == QtCore.Qt.Key_Up:
            if (parrent_item is None):
                pass
                #TODO клавиша ВВЕРХ
        if key == QtCore.Qt.Key_Down:
            print("Up")
            #TODO клавиша вниз

def handle_item_selection():
    selected_items = ui.treeWidget.selectedItems()
    if selected_items:
        selected_item = selected_items[0]
        data = selected_item.data(0, QtCore.Qt.UserRole)  # Получаем данные из пользовательской части элемента
        print("Selected Data:", data)
        position = ui.treeWidget.visualItemRect(selected_item).topRight()
        window_position = MainWindow.geometry().topLeft()
        tooltip_position = window_position + position
        QtWidgets.QToolTip.showText(tooltip_position, str(data))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.treeWidget.itemSelectionChanged.connect(handle_item_selection)

    MainWindow.show()
    sys.exit(app.exec_())

from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 500)
        MainWindow.setStatusTip("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.treeWidget = Ui_MainWindow.create_tree_from_database(self, "Local.db", "Tree")
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
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Создаем словарь, где ключом будет id узла, а значением будет список его дочерних узлов
        nodes = {}
        for row in rows:
            node_id, parent_id, position, node_type, name, data = row
            if parent_id in nodes:
                nodes[parent_id].append(row)
            else:
                nodes[parent_id] = [row]

        # Рекурсивная функция для построения дерева
        def build_tree(parent_item, parent_id):
            if parent_id in nodes:
                for row in nodes[parent_id]:
                    node_id, _, _, _, name, data = row
                    item = QtWidgets.QTreeWidgetItem(parent_item, [name])
                    item.setData(0, QtCore.Qt.UserRole, data)
                    tooltip_text = str(data)
                    item.setToolTip(0, tooltip_text)
                    build_tree(item, node_id)

        tree = MyTreeWidget(self.centralwidget)
        tree.setColumnCount(1)  # Один столбец для имени узла

        # Строим дерево начиная с корневого узла (узлов с parent_id = 0)
        build_tree(tree, 0)

        # Отображаем дерево
        tree.show()

        # Закрываем соединение с базой данных
        conn.close()
        return tree

class MyTreeWidget(QtWidgets.QTreeWidget):
    def keyPressEvent(self, event):
        key = event.key()
        current_item = self.currentItem()
        parrent_item = current_item.parent()

        if key >= QtCore.Qt.Key_1 and key <= QtCore.Qt.Key_9:
            digit = key - QtCore.Qt.Key_0
            if(parrent_item is not None and parrent_item.childCount() >= digit):
                self.setCurrentItem(current_item.parent().child(digit - 1))
            if(parrent_item is None and self.topLevelItemCount() >= digit):
                self.setCurrentItem(self.topLevelItem(digit - 1))


        # Обработка нажатия Enter для раскрытия элемента
        if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            if (current_item is not None and current_item.childCount() > 0):
                self.expandItem(current_item)
                self.setCurrentItem(current_item.child(0))


        # Обработка нажатия Backspace для возврата на уровень выше
        if key == QtCore.Qt.Key_Backspace:
            parent_item = current_item.parent()
            if parent_item is not None:
                self.setCurrentItem(parent_item)

def handle_item_selection():
    selected_items = ui.treeWidget.selectedItems()
    if selected_items:
        selected_item = selected_items[0]
        data = selected_item.data(0, QtCore.Qt.UserRole)  # Получаем данные из пользовательской части элемента
        print("Selected Data:", data)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.treeWidget.itemSelectionChanged.connect(handle_item_selection)
    MainWindow.show()
    sys.exit(app.exec_())

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from FastPasteUI import Ui_MainWindow
from TreeWidget_Class import MyTreeWidget
import sqlite3, os, PhraseEditor_Class, configparser

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
    def setupUi(self, MainWindow):
        self.mw = MainWindow

        self.config = configparser.ConfigParser()
        self.config.read(MainWindow.get_abspath("settings.ini"))

        self.treeWidget = MainWindow.create_tree_from_database("Database/Local.db", "Tree")
        header = self.treeWidget.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.treeWidget.setColumnWidth(1, 0)

        super().setupUi(MainWindow)

        if (self.config["FastPaste"]["checkbox_close"] == "1"):
            self.checkBox.setCheckState(Qt.Checked)
        else:
            self.checkBox.setCheckState(Qt.Unchecked)

        self.pushButton.clicked.connect(self.open_phrase_editor)
        self.checkBox.stateChanged.connect(self.on_state_changed)
    def create_tree_from_database(self, database_file, table_name):
        def build_tree(parent_item, parent_id):
            if parent_id in self.nodes:
                for row in self.nodes[parent_id]:
                    node_id, _, position, node_type, name, data = row
                    item = QTreeWidgetItem(parent_item, [name])
                    item.setData(0, Qt.UserRole, data)
                    item.setData(0, Qt.UserRole + 1, node_type)
                    item.setTextAlignment(1, Qt.AlignRight)
                    if(node_type == 0):
                        item.setIcon(0, QIcon(MainWindow.get_abspath(self, "Images/folder.png")))
                    if (node_type == 2):
                        item.setIcon(0, QIcon(MainWindow.get_abspath(self, "Images/file.png")))

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

            tree = MyTreeWidget()
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
            mb = QMessageBox()
            mb.setText("Не удалось найти БД")
            mb.setWindowTitle("Ошибка")
            mb.exec_()
            return MyTreeWidget()
    def get_abspath(self, name):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, name)
        return os.path.abspath(file_path)
    def open_phrase_editor(self):
        self.window = PhraseEditor_Class.PhraseEditor()
        self.window.show()
        self.mw.close()
    def on_state_changed(self):
        if(self.checkBox.isChecked()):
            self.config["FastPaste"]["checkbox_close"] = str(1)
        else:
            self.config["FastPaste"]["checkbox_close"] = str(0)
    def closeEvent(self, event):
        with open("settings.ini", 'w') as config:
            self.config.write(config)
        event.accept()

if __name__ == "__main__":
    import sys
    global app
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
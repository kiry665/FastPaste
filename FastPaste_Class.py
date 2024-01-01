from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from FastPasteUI import Ui_MainWindow
from TreeWidget_Class import MyTreeWidget

import sqlite3, os, PhraseEditor_Class, configparser, platform

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
    def setupUi(self, MainWindow):
        self.mw = MainWindow

        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(os.path.dirname(__file__),"settings.ini"))

        self.database_file = os.path.join(os.path.dirname(__file__),"Database/Local.db")
        self.table_name = "Tree"

        self.treeWidget = MainWindow.create_tree_from_database(self.database_file, self.table_name)
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

        self.quitAction = QAction('Exit', self)
        self.quitAction.triggered.connect(qApp.quit)

        self.trayIcon = QSystemTrayIcon(QIcon(os.path.join(os.path.dirname(__file__),'Images/file.png')), self)
        self.trayIcon.setToolTip('My Application')
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.quitAction)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.activated.connect(self.trayIconActivated)
        self.trayIcon.show()

        if platform.system() == 'Windows':
            import keyboard
            keyboard.add_hotkey("ctrl+u", self.on_show)
        if platform.system() == 'Linux':
            import signal
            signal.signal(signal.SIGUSR1, self.signal_handler)
            self.isSignalReceived = False
            self.timer = QTimer()
            self.timer.timeout.connect(self.check_signal)
            self.timer.start(200)
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
                            item.setIcon(0, QIcon(os.path.join(os.path.dirname(__file__),"Images/folder.png")))
                        if (node_type == 2):
                            item.setIcon(0, QIcon(os.path.join(os.path.dirname(__file__),"Images/file.png")))

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
    def open_phrase_editor(self):
        self.window = PhraseEditor_Class.PhraseEditor()
        self.window.set_mainWindow(self.mw)
        self.reload = True
        self.window.show()
        self.mw.hide()
    def on_state_changed(self):
        if(self.checkBox.isChecked()):
            self.config["FastPaste"]["checkbox_close"] = str(1)
        else:
            self.config["FastPaste"]["checkbox_close"] = str(0)
    def closeEvent(self, event):
        with open(os.path.join(os.path.dirname(__file__),"settings.ini"), 'w') as config:#Согласовано.Согласовано.
            self.config.write(config)
        event.ignore()
        self.treeWidget.tooltip.hide()
        self.hide()
    def trayIconActivated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
    def refresh_tree(self):
        self.treeWidget.setParent(None)
        self.treeWidget.deleteLater()
        self.treeWidget = self.create_tree_from_database(self.database_file, self.table_name)
        if self.treeWidget.topLevelItem(0):
            self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(0))
        header = self.treeWidget.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setVisible(False)
        self.treeWidget.setColumnWidth(1, 0)
        self.gridLayout.addWidget(self.treeWidget, 0, 0, 1, 1)
        self.treeWidget.setFocus()
    def on_show(self):
        QTimer.singleShot(0,self.show)
    def signal_handler(self, signal, frame):
        self.isSignalReceived = True
    def check_signal(self):
        if self.isSignalReceived:
            self.on_show()
        self.isSignalReceived = False

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
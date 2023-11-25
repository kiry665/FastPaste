from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QDialog, QMessageBox, QAction
from datetime import datetime
import FastPaste
import sqlite3
import DialogAddPhrase
import shutil
import os

class Ui_PhraseEditor(object):
    def setupUi(self, PhraseEditor):
        PhraseEditor.setObjectName("PhraseEditor")
        PhraseEditor.resize(500, 400)

        self.database_file = FastPaste.Ui_MainWindow.get_abspath("Database/Local.db")
        self.table_name = "Tree"

        self.centralwidget = QtWidgets.QWidget(PhraseEditor)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        self.treeWidget = self.create_tree_from_database(self.database_file, self.table_name)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().setVisible(False)

        self.textEdit = MyTextEdit(self.splitter)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setEnabled(True)

        self.splitter.setSizes([200, 300])
        self.verticalLayout.addWidget(self.splitter)
        PhraseEditor.setCentralWidget(self.centralwidget)

        self.toolBar = QtWidgets.QToolBar(PhraseEditor)
        self.toolBar.setMovable(False)
        self.toolBar.setObjectName("toolBar")

        PhraseEditor.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        self.actionaddPhrase = QtWidgets.QAction(PhraseEditor)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(FastPaste.Ui_MainWindow.get_abspath("Images/addFile.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionaddPhrase.setIcon(icon)
        self.actionaddPhrase.setObjectName("actionaddPhrase")
        self.actionaddPhrase.triggered.connect(self.addPhrase)

        self.actionremovePhrase = QtWidgets.QAction(PhraseEditor)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(FastPaste.Ui_MainWindow.get_abspath("Images/removeFile.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionremovePhrase.setIcon(icon1)
        self.actionremovePhrase.setObjectName("actionremovePhrase")
        self.actionremovePhrase.triggered.connect(self.removePhrase)

        self.actionsave = QtWidgets.QAction(PhraseEditor)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(FastPaste.Ui_MainWindow.get_abspath("Images/save.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionsave.setIcon(icon2)
        self.actionsave.setObjectName("actionsave")
        self.actionsave.triggered.connect(self.save_tree)

        self.toolBar.addAction(self.actionaddPhrase)
        self.toolBar.addAction(self.actionremovePhrase)
        self.toolBar.addAction(self.actionsave)

        self.retranslateUi(PhraseEditor)
        QtCore.QMetaObject.connectSlotsByName(PhraseEditor)
    def retranslateUi(self, PhraseEditor):
        _translate = QtCore.QCoreApplication.translate
        PhraseEditor.setWindowTitle(_translate("PhraseEditor", "Редактировать фразы"))
        self.toolBar.setWindowTitle(_translate("PhraseEditor", "toolBar"))
        self.actionaddPhrase.setText(_translate("PhraseEditor", "addPhrase"))
        self.actionremovePhrase.setText(_translate("PhraseEditor", "removePhrse"))
    def addPhrase(self):
        current_item = self.treeWidget.currentItem()

        dialog = QtWidgets.QDialog()
        ui = DialogAddPhrase.DialogAddPhrase()
        ui.setupUi(dialog)
        if dialog.exec_() == QDialog.Accepted:
            new_item = self.create_item(ui.get_name(), ui.get_type())
            if current_item is not None:
                parent_item = current_item.parent()
                root = ui.get_root()
                if root:
                    self.treeWidget.addTopLevelItem(new_item)
                else:
                    if(current_item.data(0, QtCore.Qt.UserRole+1) == 0):
                        current_item.addChild(new_item)
                    elif (current_item.data(0, QtCore.Qt.UserRole + 1) == 2):
                        if(parent_item):
                            parent_item.insertChild(parent_item.indexOfChild(current_item)+1, new_item)
                        else:
                            self.treeWidget.insertTopLevelItem(self.treeWidget.indexOfTopLevelItem(current_item)+1, new_item)
            else:
                self.treeWidget.addTopLevelItem(new_item)
                self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(0))
    def removePhrase(self):
        #reply = QtWidgets.QMessageBox.question(self.treeWidget, "Подтверждение удаления", "Вы уверены, что хотите удалить элемент? Все внутренние элементы также будут удалены.", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)\
        mb = QMessageBox()
        mb.setIcon(QMessageBox.Question)
        mb.setWindowTitle("Подтверждение удаления")
        mb.setText("Вы уверены, что хотите удалить элемент? Все внутренние элементы также будут удалены.")
        mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        mb.button(QMessageBox.Yes).setText("Да")
        buttonY = mb.button(QMessageBox.Yes)
        mb.button(QMessageBox.No).setText("Нет")
        mb.exec_()
        current_item = self.treeWidget.currentItem()
        if mb.clickedButton() == buttonY:
            if current_item is not None:
                parent = current_item.parent()
                if parent is not None:
                    parent.removeChild(current_item)
                else:
                    if self.treeWidget.topLevelItemCount() > 0:
                        self.treeWidget.takeTopLevelItem(self.treeWidget.indexOfTopLevelItem(current_item))
                        self.textEdit.setText("")
                        self.textEdit.setEnabled(False)
    def create_item(self, name, type):
        new_item = QtWidgets.QTreeWidgetItem()
        new_item.setText(0, name)
        new_item.setData(0, QtCore.Qt.UserRole, "")
        new_item.setData(0, QtCore.Qt.UserRole + 1, type)
        if type == 0:
            new_item.setIcon(0, QtGui.QIcon(FastPaste.Ui_MainWindow.get_abspath('Images/folder.png')))
        else:
            new_item.setIcon(0, QtGui.QIcon(FastPaste.Ui_MainWindow.get_abspath('Images/file.png')))
        return new_item
    def create_tree_from_database(self, database_file, table_name):
        def build_tree(parent_item, parent_id):
            if parent_id in self.nodes:
                for row in self.nodes[parent_id]:
                    node_id, _, position, node_type, name, data = row
                    item = QtWidgets.QTreeWidgetItem(parent_item, [name])
                    item.setData(0, QtCore.Qt.UserRole, data)
                    item.setData(0, QtCore.Qt.UserRole + 1, node_type)
                    item.setTextAlignment(1, Qt.AlignRight)
                    if (node_type == 0):
                        item.setIcon(0, QtGui.QIcon(FastPaste.Ui_MainWindow.get_abspath('Images/folder.png')))
                    if (node_type == 2):
                        item.setIcon(0, QtGui.QIcon(FastPaste.Ui_MainWindow.get_abspath('Images/file.png')))

                    build_tree(item, node_id)

        if (os.path.isfile(database_file)):
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

            tree = MyTreeWidget(self.splitter)
            tree.setColumnCount(1)  # Один столбец для имени узла
            # Строим дерево начиная с корневого узла (узлов с parent_id = 0)
            build_tree(tree, 0)

            conn.close()
            return tree

        else:
            mb = QtWidgets.QMessageBox()
            mb.setText("Не удалось найти БД")
            mb.setWindowTitle("Ошибка")
            mb.exec_()
            return self.MyTreeWidget(self.splitter)
    def save_tree(self):
        self.backup_database()
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM " + self.table_name)
        conn.commit()
        conn.close()
        self.start = 0
        for i in range(self.treeWidget.topLevelItemCount()):
            root_item = self.treeWidget.topLevelItem(i)
            self.traverse_tree(root_item,position=i+1)
    def traverse_tree(self, root, parent_id=0, position=1):
        self.start += 1
        node_id = self.start
        # Обработка текущего элемента
        node_type = root.data(0, Qt.UserRole+1)
        name = root.text(0)
        data = root.data(0, Qt.UserRole)

        #print(node_id, parent_id, position, node_type, name, data)

        #Создание соединения с БД
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        # Запись данных в таблицу
        cursor.execute(
            "INSERT INTO " + self.table_name + " (id, pid, pos, type, name, data) VALUES (?, ?, ?, ?, ?, ?)",
            (node_id, parent_id, position, node_type, name, data)
        )

        # Закрытие соединения с БД
        conn.commit()
        conn.close()

        # Рекурсивный вызов для дочерних элементов
        for index in range(root.childCount()):
            child = root.child(index)
            self.traverse_tree(child, parent_id=node_id if parent_id is not None else 0, position=index+1)
    def backup_database(self):
        now = datetime.now()
        current_time = now.strftime("%d.%m.%y %H.%M")
        backup_root = FastPaste.Ui_MainWindow.get_abspath("Database/Backup")
        root, extension = os.path.splitext(self.database_file)
        shutil.copyfile(self.database_file, backup_root + "_backup "+ current_time + extension)

class MyTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super(MyTreeWidget, self).__init__(parent)
        self.setDragDropMode(MyTreeWidget.InternalMove)
        self.currentItemChanged.connect(self.handle_item_change)
    def dropEvent(self, e):
        item = self.itemAt(e.pos())
        drop_indicator_position = self.dropIndicatorPosition()

        if item and (item.data(0, QtCore.Qt.UserRole+1) == 0 or drop_indicator_position == QtWidgets.QAbstractItemView.AboveItem or drop_indicator_position == QtWidgets.QAbstractItemView.BelowItem):
            super(MyTreeWidget, self).dropEvent(e)
        else:
            e.ignore()

            MyTreeWidget.moveItem(self, self.currentItem(),item)
    def keyPressEvent(self, event):
        super(MyTreeWidget, self).keyPressEvent(event)
        key = event.key()
        current_item = self.currentItem()
        parrent_item = current_item.parent()

        # Обработка нажатия Enter для раскрытия элемента или вставки текста
        if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            if (current_item is not None and current_item.childCount() > 0):
                if current_item.isExpanded():
                    self.setCurrentItem(current_item.child(0))
                else:
                    self.expandItem(current_item)


        # Обработка нажатия Backspace для возврата на уровень выше
        if key == QtCore.Qt.Key_Backspace:
            parent_item = current_item.parent()
            if parent_item is not None:
                self.setCurrentItem(parent_item)
    def moveItem(self, sourceItem, targetItem):
        if targetItem is not None:
            sourceParent = sourceItem.parent()
            if sourceParent is not None:
                sourceParent.removeChild(sourceItem)
            else:
                sourceIndex = self.indexOfTopLevelItem(sourceItem)
                self.takeTopLevelItem(sourceIndex)

            if targetItem.parent():
                targetItem.parent().insertChild(targetItem.parent().indexOfChild(targetItem)+1,sourceItem)
            else:
                self.insertTopLevelItem(self.indexOfTopLevelItem(targetItem)+1,sourceItem)
    def handle_item_change(self, current, previous):
        textEdit = self.window().findChild(QtWidgets.QTextEdit)
        #lineEdit.setText("Find")
        if current:
            if(current.data(0, QtCore.Qt.UserRole+1) == 0):
               textEdit.setEnabled(False)
            elif(current.data(0, QtCore.Qt.UserRole+1) == 2):
                textEdit.setEnabled(True)

            textEdit.setText(current.data(0, QtCore.Qt.UserRole))

class MyTextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.treeWidget = self.window().findChild(QtWidgets.QTreeWidget)
        self.textChanged.connect(self.on_text_changed)
    def on_text_changed(self):
        current_item = self.treeWidget.currentItem()
        if current_item:
            current_item.setData(0, QtCore.Qt.UserRole, self.toPlainText())

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PhraseEditor = QtWidgets.QMainWindow()
    ui = Ui_PhraseEditor()
    ui.setupUi(PhraseEditor)
    PhraseEditor.show()
    sys.exit(app.exec_())

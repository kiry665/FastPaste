from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QDialog
from FastPaste import Ui_MainWindow
import sqlite3
import DialogAddPhrase


class Ui_PhraseEditor(object):

    def setupUi(self, PhraseEditor):
        PhraseEditor.setObjectName("PhraseEditor")
        PhraseEditor.resize(500, 400)

        self.centralwidget = QtWidgets.QWidget(PhraseEditor)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        self.treeWidget = self.create_tree_from_database(Ui_MainWindow.get_abspath("Local.db"), "Tree")
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().setVisible(False)

        self.textEdit = QtWidgets.QTextEdit(self.splitter)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setText("hgfjh")

        self.splitter.setSizes([200, 300])
        self.verticalLayout.addWidget(self.splitter)
        PhraseEditor.setCentralWidget(self.centralwidget)

        self.toolBar = QtWidgets.QToolBar(PhraseEditor)
        self.toolBar.setMovable(False)
        self.toolBar.setObjectName("toolBar")

        PhraseEditor.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        self.actionaddPhrase = QtWidgets.QAction(PhraseEditor)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(Ui_MainWindow.get_abspath("Images/addFile.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionaddPhrase.setIcon(icon)
        self.actionaddPhrase.setObjectName("actionaddPhrase")
        self.actionaddPhrase.triggered.connect(self.addPhrase)

        self.actionremovePhrase = QtWidgets.QAction(PhraseEditor)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(Ui_MainWindow.get_abspath("Images/removeFile.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionremovePhrase.setIcon(icon1)
        self.actionremovePhrase.setObjectName("actionremovePhrase")

        self.toolBar.addAction(self.actionaddPhrase)
        self.toolBar.addAction(self.actionremovePhrase)

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
        parent_item = current_item.parent()
        dialog = QtWidgets.QDialog()
        ui = DialogAddPhrase.DialogAddPhrase()
        ui.setupUi(dialog)
        if dialog.exec_() == QDialog.Accepted:
            new_item = self.create_item(ui.get_name(), ui.get_type())
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


    def create_item(self, name, type):
        new_item = QtWidgets.QTreeWidgetItem()
        new_item.setText(0, name)
        new_item.setData(0, QtCore.Qt.UserRole, "")
        new_item.setData(0, QtCore.Qt.UserRole + 1, type)
        if type == 0:
            new_item.setIcon(0, QtGui.QIcon(Ui_MainWindow.get_abspath('Images/folder.png')))
        else:
            new_item.setIcon(0, QtGui.QIcon(Ui_MainWindow.get_abspath('Images/file.png')))
        return new_item

    def create_tree_from_database(self, database_file, table_name):
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

        # Рекурсивная функция для построения дерева
        def build_tree(parent_item, parent_id):
            if parent_id in self.nodes:
                for row in self.nodes[parent_id]:
                    node_id, _, position, node_type, name, data = row
                    item = QtWidgets.QTreeWidgetItem(parent_item, [name])
                    item.setData(0, QtCore.Qt.UserRole, data)
                    item.setData(0, QtCore.Qt.UserRole + 1, node_type)
                    item.setTextAlignment(1, Qt.AlignRight)
                    if (node_type == 0):
                        item.setIcon(0, QtGui.QIcon(Ui_MainWindow.get_abspath('Images/folder.png')))
                    if (node_type == 2):
                        item.setIcon(0, QtGui.QIcon(Ui_MainWindow.get_abspath('Images/file.png')))

                    build_tree(item, node_id)

        tree = MyTreeWidget(self.splitter)

        # Строим дерево начиная с корневого узла (узлов с parent_id = 0)
        build_tree(tree, 0)

        conn.close()
        return tree

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
        if(current.data(0, QtCore.Qt.UserRole+1) == 0):
            ui.textEdit.setEnabled(False)
        elif(current.data(0, QtCore.Qt.UserRole+1) == 2):
            ui.textEdit.setEnabled(True)
        if previous:
            text = ui.textEdit.toPlainText()
            previous.setData(0, QtCore.Qt.UserRole, text)
        if current:
            ui.textEdit.setText(current.data(0, QtCore.Qt.UserRole))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PhraseEditor = QtWidgets.QMainWindow()
    ui = Ui_PhraseEditor()
    ui.setupUi(PhraseEditor)
    PhraseEditor.show()
    sys.exit(app.exec_())

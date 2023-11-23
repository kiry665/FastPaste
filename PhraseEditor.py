from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
import FastPaste
import sqlite3


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

        #self.treeWidget = QtWidgets.QTreeWidget(self.splitter)
        self.treeWidget = self.create_tree_from_database(FastPaste.Ui_MainWindow.get_abspath("Local.db"), "Tree")
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().setVisible(False)
        #self.treeWidget.setDragEnabled(True)
        #self.treeWidget.setAcceptDrops(True)
        #self.treeWidget.setDragDropMode(self.treeWidget.InternalMove)

        self.textEdit = QtWidgets.QTextEdit(self.splitter)
        self.textEdit.setObjectName("textEdit")

        self.splitter.setSizes([200, 300])
        self.verticalLayout.addWidget(self.splitter)
        PhraseEditor.setCentralWidget(self.centralwidget)

        self.toolBar = QtWidgets.QToolBar(PhraseEditor)
        self.toolBar.setMovable(False)
        self.toolBar.setObjectName("toolBar")

        PhraseEditor.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        self.actionaddPhrase = QtWidgets.QAction(PhraseEditor)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Images/addFile.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionaddPhrase.setIcon(icon)
        self.actionaddPhrase.setObjectName("actionaddPhrase")
        self.actionremovePhrase = QtWidgets.QAction(PhraseEditor)

        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("Images/removeFile.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
                        item.setIcon(0, QtGui.QIcon(FastPaste.Ui_MainWindow.get_abspath('Images/folder.png')))
                    if (node_type == 2):
                        item.setIcon(0, QtGui.QIcon(FastPaste.Ui_MainWindow.get_abspath('Images/file.png')))

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

    def dropEvent(self, e):
        item = self.itemAt(e.pos())
        drop_indicator_position = self.dropIndicatorPosition()

        if item and (item.data(0, QtCore.Qt.UserRole+1) == 0 or drop_indicator_position == QtWidgets.QAbstractItemView.AboveItem or drop_indicator_position == QtWidgets.QAbstractItemView.BelowItem):
            super(MyTreeWidget, self).dropEvent(e)
        else:
            e.ignore()

            MyTreeWidget.moveItem(self, self.currentItem(),item)

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

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PhraseEditor = QtWidgets.QMainWindow()
    ui = Ui_PhraseEditor()
    ui.setupUi(PhraseEditor)
    PhraseEditor.show()
    sys.exit(app.exec_())

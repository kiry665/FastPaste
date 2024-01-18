from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PhraseEditorUI import Ui_PhraseEditor
from DialogAddPhrase_Class import DialogAddPhrase
from UndoRedo_Class import UndoRedo
import sqlite3, shutil, datetime, os, configparser
import res_rc

class PhraseEditor(QMainWindow, Ui_PhraseEditor):
    def __init__(self, parent=None):
        super(PhraseEditor, self).__init__(parent)
        self.setupUi(self)
    def setupUi(self, PhraseEditor):
        self.database_file = os.path.join(os.path.dirname(__file__),"Database/Local.db")
        self.table_name = "Tree"
        self.treeWidget = self.create_tree_from_database(self.database_file, self.table_name)
        self.textEdit = PhraseEdit()
        self.lineEdit = NameEdit()
        super().setupUi(PhraseEditor)
        self.treeWidget.setParent(self.splitter)
        self.splitter.insertWidget(0, self.treeWidget)
        self.textEdit.setEnabled(False)

        self.actionaddPhrase.triggered.connect(self.addPhrase)
        self.actionremovePhrase.triggered.connect(self.removePhrase)
        self.actionsave.triggered.connect(self.save_tree)
        self.actionback.triggered.connect(self.back)
        self.actionforward.triggered.connect(self.forward)

        self.actionback.setDisabled(True)
        self.actionforward.setDisabled(True)

        self.undoredo = UndoRedo(self.actionback, self.actionforward)
        self.hidden_items = []
    def set_mainWindow(self, mw):
        self.mw = mw
    def addPhrase(self):
        current_item = self.treeWidget.currentItem()
        dialog = QDialog()
        ui = DialogAddPhrase()
        ui.setupUi(dialog)
        if dialog.exec_() == QDialog.Accepted:
            new_item = self.create_item(ui.get_name(), ui.get_type())
            self.undoredo.push_undo(new_item, 1)
            if current_item is not None:
                parent_item = current_item.parent()
                root = ui.get_root()
                if root:
                    self.treeWidget.addTopLevelItem(new_item)
                else:
                    if(current_item.data(0, Qt.UserRole+1) == 0):
                        current_item.addChild(new_item)
                    elif (current_item.data(0, Qt.UserRole + 1) == 2):
                        if(parent_item):
                            parent_item.insertChild(parent_item.indexOfChild(current_item)+1, new_item)
                        else:
                            self.treeWidget.insertTopLevelItem(self.treeWidget.indexOfTopLevelItem(current_item)+1, new_item)
            else:
                self.treeWidget.addTopLevelItem(new_item)
                self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(0))
    def removePhrase(self):
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
            current_item.setHidden(True)
            self.hidden_items.append(current_item)
            self.undoredo.push_undo(current_item, 0)
    def create_item(self, name, type):
        new_item = QTreeWidgetItem()
        new_item.setText(0, name)
        new_item.setData(0, Qt.UserRole, "")
        new_item.setData(0, Qt.UserRole + 1, type)
        if type == 0:
            new_item.setIcon(0, QIcon(os.path.join(os.path.dirname(__file__),'Images/folder.png')))
        else:
            new_item.setIcon(0, QIcon(os.path.join(os.path.dirname(__file__),'Images/file.png')))
        return new_item
    def create_tree_from_database(self, database_file, table_name):
        def build_tree(parent_item, parent_id):
            if parent_id in self.nodes:
                for row in self.nodes[parent_id]:
                    node_id, _, position, node_type, name, data = row
                    item = QTreeWidgetItem(parent_item, [name])
                    item.setData(0, Qt.UserRole, data)
                    item.setData(0, Qt.UserRole + 1, node_type)
                    item.setTextAlignment(1, Qt.AlignRight)
                    if (node_type == 0):
                        icon = QIcon()
                        icon.addPixmap(QPixmap(":/Images/Images/folder.png"))
                        item.setIcon(0, icon)
                    if (node_type == 2):
                        icon = QIcon()
                        icon.addPixmap(QPixmap(":/Images/Images/file.png"))
                        item.setIcon(0, icon)

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

            tree = MyTreeWidget()
            tree.setColumnCount(1)  # Один столбец для имени узла
            tree.header().setVisible(False)
            # Строим дерево начиная с корневого узла (узлов с parent_id = 0)
            build_tree(tree, 0)
            conn.close()
            return tree
        else:
            mb = QMessageBox()
            mb.setText("Не удалось найти БД")
            mb.setWindowTitle("Ошибка")
            mb.exec_()
            return self.MyTreeWidget(self.splitter)
    def save_tree(self):
        self.backup_database()
        self.remove_hidden_items()
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
        now = datetime.datetime.now()
        current_time = now.strftime("%d.%m.%y %H.%M")
        backup_root = os.path.join(os.path.dirname(__file__),"Database/Backup")
        root, extension = os.path.splitext(self.database_file)
        shutil.copyfile(self.database_file, backup_root + "_backup "+ current_time + extension)
    def remove_hidden_items(self):
        for current_item in self.hidden_items:
            if current_item is not None:
                parent = current_item.parent()
                if parent is not None:
                    parent.removeChild(current_item)
                else:
                    if self.treeWidget.topLevelItemCount() > 0:
                        self.treeWidget.takeTopLevelItem(self.treeWidget.indexOfTopLevelItem(current_item))
                        self.textEdit.setText("")
                        self.textEdit.setEnabled(False)
    def closeEvent(self, event, QCloseEvent=None):
        self.mw.refresh_tree()
        self.mw.show()
        event.accept()
    def back(self):
        if not self.undoredo.undo_is_empty():
            element = self.undoredo.pop_undo()
            if element[1] == 0:
                element[0].setHidden(False)
                index_to_remove = self.hidden_items.index(element[0])
                self.hidden_items.pop(index_to_remove)
            else:
                element[0].setHidden(True)
                self.hidden_items.append(element[0])
    def forward(self):
        if not self.undoredo.redo_is_empty():
            element = self.undoredo.pop_redo()
            if element[1] == 0:
                element[0].setHidden(True)
                self.hidden_items.append(element[0])
            else:
                element[0].setHidden(False)
                index_to_remove = self.hidden_items.index(element[0])
                self.hidden_items.pop(index_to_remove)

class MyTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super(MyTreeWidget, self).__init__(parent)
        self.setDragDropMode(MyTreeWidget.InternalMove)
        self.currentItemChanged.connect(self.handle_item_change)
        self.itemCollapsed.connect(self.itemCollapse)
    def dropEvent(self, e):
        item = self.itemAt(e.pos())
        drop_indicator_position = self.dropIndicatorPosition()
        if item and (item.data(0, Qt.UserRole+1) == 0 or drop_indicator_position == QAbstractItemView.AboveItem or drop_indicator_position == QAbstractItemView.BelowItem):
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
        if key == Qt.Key_Return or key == Qt.Key_Enter:
            if (current_item is not None and current_item.childCount() > 0):
                if current_item.isExpanded():
                    self.setCurrentItem(current_item.child(0))
                else:
                    self.expandItem(current_item)
        # Обработка нажатия Backspace для возврата на уровень выше
        if key == Qt.Key_Backspace:
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
        textEdit = self.window().findChild(QTextEdit)
        textLine = self.window().findChild(QLineEdit)
        if current:
            if(current.data(0, Qt.UserRole+1) == 0):
                textEdit.setEnabled(False)
                textEdit.setText("")
            elif(current.data(0, Qt.UserRole+1) == 2):
                textEdit.setEnabled(True)
                textEdit.setText(current.data(0, Qt.UserRole))

            current_item = self.currentItem()
            textLine.setText(current_item.text(0))
            textLine.setCursorPosition(0)
    def itemCollapse(self, item):
        self.setCurrentItem(item)
class PhraseEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.textChanged.connect(self.on_text_changed)
    def on_text_changed(self):
        current_item = self.window().findChild(QTreeWidget).currentItem()
        if current_item:
            current_item.setData(0, Qt.UserRole, self.toPlainText())
class NameEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.textChanged.connect(self.on_text_changed)
    def on_text_changed(self):
        current_item = self.window().findChild(QTreeWidget).currentItem()
        current_item.setText(0, self.text())

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_window = PhraseEditor()
    main_window.show()
    sys.exit(app.exec_())
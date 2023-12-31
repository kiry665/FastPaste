from DialogAddPhraseUI import Ui_Dialog
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
class DialogAddPhrase(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(DialogAddPhrase, self).__init__(parent)
        self.setupUi(self)

    def setupUi(self, Dialog):
        super().setupUi(Dialog)
        self.buttonBox.accepted.connect(self.name_accept)
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Ок")
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Отмена")

    def name_accept(self):
        if(self.get_name()):
            self.dialog.accept()
        else:
            mb = QMessageBox()
            mb.setText("Введите имя записи")
            mb.setWindowTitle("Ошибка")
            mb.exec_()

    def get_name(self):
        return self.lineEdit.text()

    def get_type(self):
        if(self.radioButton.isChecked()):
            type = 0
        else:
            type = 2
        return type

    def get_root(self):
        if(self.checkBox.isChecked()):
            return True
        else:
            return False

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Dialog = DialogAddPhrase()
    Dialog.show()
    sys.exit(app.exec_())
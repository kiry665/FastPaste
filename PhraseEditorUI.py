from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PhraseEditor(object):
    def setupUi(self, PhraseEditor):
        PhraseEditor.setObjectName("PhraseEditor")
        PhraseEditor.resize(500, 400)
        self.centralwidget = QtWidgets.QWidget(PhraseEditor)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.treeWidget = QtWidgets.QTreeWidget(self.splitter)
        self.treeWidget.setObjectName("treeWidget")
        self.textEdit = QtWidgets.QTextEdit(self.splitter)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
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
        self.actionsave = QtWidgets.QAction(PhraseEditor)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("Images/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionsave.setIcon(icon2)
        self.actionsave.setObjectName("actionsave")
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
        self.actionsave.setText(_translate("PhraseEditor", "save"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PhraseEditor = QtWidgets.QMainWindow()
    ui = Ui_PhraseEditor()
    ui.setupUi(PhraseEditor)
    PhraseEditor.show()
    sys.exit(app.exec_())

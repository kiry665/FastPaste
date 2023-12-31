from PyQt5.QtWidgets import *
from FastPaste_Class import MainWindow

if __name__ == "__main__":
    import sys
    global app
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
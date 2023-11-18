from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import os
import keyboard
import logging
import threading

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

def application():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())

if(__name__ == "__main__"):
    application()

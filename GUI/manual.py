from PyQt5 import QtWidgets,QtGui
from PyQt5.QtWidgets import QApplication,QMainWindow

import sys

def window() :
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setGeometry(200,200,400,300)
    window.setWindowTitle("TEST")
    window.setMinimumSize(400,300)
    window.setMaximumSize(800,600)
    window.setWindowIcon(QtGui.QIcon("/Users/kaswat/Downloads/LINEwhoscall.png"))
    window.show()
    sys.exit(app.exec_())

window()
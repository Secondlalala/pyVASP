# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MyApp(object):
    def setupUi(self, MyApp):
        MyApp.setObjectName("MyApp")
        MyApp.setEnabled(True)
        MyApp.resize(300, 350)
        MyApp.setMinimumSize(QtCore.QSize(300, 350))
        MyApp.setMaximumSize(QtCore.QSize(400, 450))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../../../Users/kaswat/Downloads/1200px-LINEwhoscall_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MyApp.setWindowIcon(icon)
        MyApp.setAutoFillBackground(False)
        self.centralwidget = QtWidgets.QWidget(MyApp)
        self.centralwidget.setObjectName("centralwidget")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(20, 40, 261, 131))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(2)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(1, 1, item)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(12, 12, 271, 16))
        self.label.setAutoFillBackground(True)
        self.label.setObjectName("label")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 250, 281, 51))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton.setStyleSheet("color:rgb(0, 0, 255)")
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton_2.setStyleSheet("color:rgb(255, 0, 0)\n"
"")
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.formLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.formLayoutWidget.setGeometry(QtCore.QRect(9, 180, 281, 31))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.lineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit)
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(110, 220, 87, 20))
        self.checkBox.setObjectName("checkBox")
        MyApp.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MyApp)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 300, 22))
        self.menubar.setObjectName("menubar")
        MyApp.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MyApp)
        self.statusbar.setEnabled(False)
        self.statusbar.setObjectName("statusbar")
        MyApp.setStatusBar(self.statusbar)

        self.retranslateUi(MyApp)
        self.pushButton.clicked.connect(self.checkBox.toggle)
        self.lineEdit.textEdited['QString'].connect(self.tableWidget.resizeRowsToContents)
        QtCore.QMetaObject.connectSlotsByName(MyApp)

    def retranslateUi(self, MyApp):
        _translate = QtCore.QCoreApplication.translate
        MyApp.setWindowTitle(_translate("MyApp", "My Application"))
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("MyApp", "New Row"))
        item = self.tableWidget.verticalHeaderItem(1)
        item.setText(_translate("MyApp", "New Row"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MyApp", "New Column"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MyApp", "New Column"))
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)
        item = self.tableWidget.item(0, 0)
        item.setText(_translate("MyApp", "11"))
        item = self.tableWidget.item(0, 1)
        item.setText(_translate("MyApp", "22"))
        item = self.tableWidget.item(1, 0)
        item.setText(_translate("MyApp", "33"))
        item = self.tableWidget.item(1, 1)
        item.setText(_translate("MyApp", "44"))
        self.tableWidget.setSortingEnabled(__sortingEnabled)
        self.label.setText(_translate("MyApp", "Test GUI program by Python"))
        self.pushButton.setText(_translate("MyApp", "OK"))
        self.pushButton_2.setToolTip(_translate("MyApp", "<html><head/><body><p><span style=\" font-size:14pt;\">Cancel all change and exit.</span></p></body></html>"))
        self.pushButton_2.setText(_translate("MyApp", "Cancel"))
        self.label_2.setText(_translate("MyApp", "Number"))
        self.checkBox.setText(_translate("MyApp", "CheckBox"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MyApp = QtWidgets.QMainWindow()
    ui = Ui_MyApp()
    ui.setupUi(MyApp)
    MyApp.show()
    sys.exit(app.exec_())

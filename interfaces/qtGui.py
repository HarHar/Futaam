# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qtGui.ui'
#
# Created: Wed Jan  9 22:00:32 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Futaam(object):
    def setupUi(self, Futaam):
        Futaam.setObjectName(_fromUtf8("Futaam"))
        Futaam.resize(790, 595)
        self.centralwidget = QtGui.QWidget(Futaam)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.columnView = QtGui.QColumnView(self.centralwidget)
        self.columnView.setGeometry(QtCore.QRect(10, 10, 771, 481))
        self.columnView.setObjectName(_fromUtf8("columnView"))
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(20, 510, 86, 27))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(700, 510, 86, 27))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.pushButton_3 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(120, 510, 86, 27))
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        Futaam.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(Futaam)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 790, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        Futaam.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(Futaam)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        Futaam.setStatusBar(self.statusbar)

        self.retranslateUi(Futaam)
        QtCore.QMetaObject.connectSlotsByName(Futaam)

    def retranslateUi(self, Futaam):
        Futaam.setWindowTitle(QtGui.QApplication.translate("Futaam", "Fuutam", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Futaam", "Add Entry", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("Futaam", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("Futaam", "Delete Entry", None, QtGui.QApplication.UnicodeUTF8))


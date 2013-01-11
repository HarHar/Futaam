#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from PyQt4 import QtGui
from PyQt4 import QtCore
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
import interfaces.qtGui
from interfaces.common import *

class TableModel(QtCore.QAbstractTableModel):
	def __init__(self):
		super(TableModel, self).__init__()
		self.animeList = []
		self.headers = ["Title","Genre","Status","Watched","Observations"]

	def columnCount(self, parent = QtCore.QModelIndex()):
		return 5

	def data(self, index, role = QtCore.Qt.DisplayRole):
		if index.isValid() == False:
			return QtCore.QVariant()
		if index.row() >= self.rowCount() or index.row() < 0:
			return QtCore.QVariant()

		if role == QtCore.Qt.DisplayRole:
			if index.column() == 0:
				return self.animeList[index.row()][0]
			elif index.column() == 1:
				return self.animeList[index.row()][1]
			elif index.column() == 2:
				return self.animeList[index.row()][2]
			elif index.column() == 3:
				return self.animeList[index.row()][3]
			elif index.column() == 4:
				return self.animeList[index.row()][4]

		return QtCore.QVariant()

	def headerData(self, column, orientation, role = QtCore.Qt.DisplayRole):
		if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
			return QtCore.QVariant(self.headers[column])
		return QtCore.QVariant()

	def rowCount(self, parent = QtCore.QModelIndex()):
		return len(self.animeList)

	def load_db(self, filename):
		self.db = Parser(filename)
		for entry in self.db.dictionary['items']:
			self.animeList.append([entry["name"], entry["genre"], entry["status"], entry["lastwatched"], entry["obs"]])

def main(argv):
	print('GUI interface. Arguments: ')
	print(repr(argv))

	app = QtGui.QApplication(argv)
	window = QtGui.QMainWindow()
	ui = interfaces.qtGui.Ui_Futaam()
	ui.setupUi(window)

	model = TableModel()
	model.load_db(argv[0])
	ui.tableView.setModel(model)

	QtCore.QObject.connect(ui.actionQuit, QtCore.SIGNAL(_fromUtf8("triggered()")), window.close)

	window.show()

	exit(app.exec_())

def help():
	return 'Help page for Qt interface'

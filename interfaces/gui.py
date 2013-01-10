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

import interfaces.qtGui
from PyQt4 import Qt
from PyQt4 import QtGui
from PyQt4 import QtCore

class TableModel(QtCore.QAbstractTableModel):
	def __init__(self):
		self.animuList = [["Best Anime","x","y","z","q"]]
		return

	def columnCount(self):
		return 4

	def data(self, index, role = Qt.DisplayRole):
		if index.isValid() == False:
			return QtCore.QVariant()
		if index.row() >= self.rowCount() or index.row() < 0:
			return QtCore.QVariant()

		if role == Qt.DisplayRole:
			if index.column() == 0:
				return animuList[0][index.row()]
			elif index.column() == 1:
				return animuList[1][index.row()]
			elif index.column() == 2:
				return animuList[2][index.row()]
			elif index.column() == 3:
				return animuList[3][index.row()]
			elif index.column() == 4:
				return animuList[4][index.row()]

		return QtCore.QVariant()

	def headerData(self, section, orientation, role):
		if role == QtCore.DisplayRole():
			if orientation == Qt.Horizontal:
				if section == 0:
					return "Title"
				elif section == 1:
					return "Genre"
				elif section == 2:
					return "Status"
				elif section == 3:
					return "Episodes Watched"
				elif section == 4:
					return "Observations"
		return QtCore.QVariant

	def rowCount(self):
		return 0

def main(argv):
	print('GUI interface. Arguments: ')
	print(repr(argv))

	model = TableModel()
	model.setColumnCount(5)
	#model.insertRow(1,["Anime","25","Watched","Awesome","Cool show"])

	app = QtGui.QApplication(argv)
	window = QtGui.QMainWindow()
	ui = interfaces.qtGui.Ui_Futaam()
	ui.setupUi(window)
	ui.tableView.setModel(model)
	window.show()

	exit(app.exec_())

def help():
	return 'Help page for Qt interface'

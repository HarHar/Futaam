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

class gui(QtGui.QWidget):

	def __init__(self):
		super(gui, self).__init__()

		self.initUI()

	def initUI(self):
		self.resize(250, 150)
		self.move(300, 300)
		self.setWindowTitle("Futaam")
		QtGui.QLabel(text="Your Animu here", parent=self)
		self.show()

def main(argv):
	print('GUI interface. Arguments: ')
	print(repr(argv))

	app = QtGui.QApplication(argv)
	w = gui()
	exit(app.exec_())

def help():
	return 'Help page for Qt interface'
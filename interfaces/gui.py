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
from PyQt4 import uic
from interfaces.common import *

dbfile = []
host = ''
port = 8500
dbs = []

class TableModel(QtCore.QAbstractTableModel):
	def __init__(self):
		super(TableModel, self).__init__()
		self.animeList = []
		self.headers = ["Title","Genre","Status","Watched","Observations"]
		self.active_file = ""

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

	def getAnimeNames(self):
		names = []
		for anime in self.animeList:
			names.append(anime[0])
		return names

	def headerData(self, column, orientation, role = QtCore.Qt.DisplayRole):
		if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
			return QtCore.QVariant(self.headers[column])
		return QtCore.QVariant()

	def rowCount(self, parent = QtCore.QModelIndex()):
		return len(self.animeList)

	def load_db(self, fl, db):
		self.active_file = fl
		self.db = db
		for entry in self.db.dictionary['items']:
			self.animeList.append([entry["name"], entry["genre"], translated_status[entry['type'].lower()][entry["status"].lower()], entry["lastwatched"], entry["obs"]])
	
	def cbIndexToStatus(self, index):
		if index == 0:
			return 'w'
		elif index == 1:
			return 'q'
		elif index == 2:
			return 'd'
		elif index == 3:
			return 'c'
		else:
			return 'h'
			
class AddEntryDialog(QtGui.QDialog):
	def __init__(self, parent = None):
		QtGui.QDialog.__init__(self, parent)
		self.setWindowTitle("Add Entry")
		self.ui = uic.loadUi("./interfaces/ui/addDialog.ui", self)
		self.ui.show()

		self.ui.statusSelect.addItems(["Watched", "Queued", "Dropped", "Watching", "On Hold"])
		QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.add)
		QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("rejected()"), self.close)
		QtCore.QObject.connect(self.titleLine, QtCore.SIGNAL("editingFinished()"), self.populateCB)
		QtCore.QObject.connect(self.resultSelect, QtCore.SIGNAL("currentIndexChanged()"), self.animeSelected)

	def populateCB(self):
		self.resultSelect.clear()
		title = self.titleLine.text()
		if self.ui.animeButton.isChecked() == True:
			search_results = utils.MALWrapper.search(title, "anime")
		else:
			search_results = utils.MALWrapper.search(title, "manga")
		for result in search_results:
			self.resultSelect.addItem(str(result["title"]))
		self.results = search_results

	def animeSelected(self, index):
		return

	def add(self):
		return

class DeleteEntryDialog(QtGui.QDialog):
	def __init__(self, parent = None, names = []):
		QtGui.QDialog.__init__(self, parent)
		self.ui = uic.loadUi("./interfaces/ui/deleteDialog.ui", self)
		self.ui.show()

		self.selectBox.addItems(names)
		QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.delete)
		QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("rejected()"), self.close)

	def delete(self):
		doDelete(self.ui.selectBox.currentIndex())
		self.done(0)

class SwapEntryDialog(QtGui.QDialog):
	def __init__(self, parent = None, names = []):
		QtGui.QDialog.__init__(self, parent)
		self.ui = uic.loadUi("./interfaces/ui/swapDialog.ui", self)
		self.ui.show()

		self.ui.selectBox1.addItems(names)
		self.ui.selectBox2.addItems(names)
		QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.swap)
		QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("rejected()"), self.close)
		
	def swap(self):
		entry1 = self.selectBox1.currentIndex()
		entry2 = self.selectBox2.currentIndex()
		if entry1 == entry2:
			self.done(0)
		doSwap(entry1, entry2)
		self.done(0)

class EditEntryDialog(QtGui.QDialog):
	def __init__(self, parent=None, names=None, entries=None):
		QtGui.QDialog.__init__(self, parent)
		self.entries = entries
		self.ui = uic.loadUi("./interfaces/ui/editDialog.ui", self)
		self.ui.show()

		self.ui.entrySelect.addItems(names)
		self.ui.statusSelect.addItems(["Watched", "Queued", "Dropped", "Watching", "On Hold"])
		QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.edit)
		QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("rejected()"), self.close)
		QtCore.QObject.connect(self.ui.entrySelect, QtCore.SIGNAL("currentIndexChanged(int)"), self.fillEntries)
		self.fillEntries()

	def fillEntries(self, index=0):
		self.index = index
		self.currentEntry = self.entries[self.index]
		self.ui.titleLine.setText(self.currentEntry['name'])
		self.ui.obsLine.setText(self.currentEntry['obs'])
		self.ui.episodesSelect.setValue(int(self.currentEntry['lastwatched']))
		self.ui.genreLine.setText(self.currentEntry['genre'])

	def edit(self):
		doEdit(self.index, self.ui.titleLine.text(), self.ui.obsLine.text(), 
			self.ui.statusSelect.currentIndex(), self.ui.episodesSelect.value(),
			self.ui.genreLine.text())
		return

def openFile():
	global model
	filename = QtGui.QFileDialog.getOpenFileName(None, "Open Data File", "", "Futaam Database (*.db);; All Files (*)")
	if filename != None:
		model = TableModel()
		model.load_db(filename, parser.Parser(filename))
		ui.tableView.setModel(model)

def deleteEntry():
	global model
	global ui
	
	dialog = DeleteEntryDialog(parent=ui.centralwidget, names=model.getAnimeNames())
	toDelete = dialog.exec_()

def doDelete(index):
	global model 
	entry = model.db.dictionary['items'][index]
	model.db.dictionary['items'].remove(entry)
	model.db.dictionary['count'] -= 1
	rebuildIds()
	reloadTable()

def addEntry():
	global ui
	
	dialog = AddEntryDialog(parent=ui.centralwidget)
	dialog.exec_()

def swapEntries():
	global model
	global ui

	dialog = SwapEntryDialog(names=model.getAnimeNames(), parent=ui.centralwidget)
	dialog.exec_()

def editEntry():
	global modal
	global ui
	dialog = EditEntryDialog(parent=ui.centralwidget, names=model.getAnimeNames(), entries=model.db.dictionary['items'])
	dialog.exec_()

def doSwap(index1, index2):
	global model

	entry1 = model.db.dictionary['items'][index1]
	entry2 = model.db.dictionary['items'][index2]
	model.db.dictionary['items'][index1] = entry2
	model.db.dictionary['items'][index2] = entry1
	rebuildIds()
	reloadTable()

def doEdit(index, title, obs, status, eps, genre):
	global model
	entry = model.db.dictionary['items'][index]
	# NOTE: The string we've gotten back from Qt
	# functions are QStrings and need to be converted
	# back into regular ones before we can save them
	entry['name'] = str(title)
	entry['obs'] = str(obs)
	entry['lastwatched'] = str(eps)
	entry['status']= model.cbIndexToStatus(status)
	entry['genre'] = str(genre)
	model.db.save()
	reloadTable()

def rebuildIds():
	global model
	for x in xrange(0, model.db.dictionary['count']):
		model.db.dictionary['items'][x]['id'] = x
	model.db.save()

def reloadTable():
	global model
	global ui
	global dbs
	global dbfile
	global port
	global host
	filename = model.active_file
	model = TableModel()
	if host == '':
		model.load_db(filename, parser.Parser(dbfile[0]))
	else:
		if password == '':
			print colors.fail + 'Missing password! ' + colors.default + 'Use "--password [pass]"'
			sys.exit(1)
		model.load_db(filename, parser.Parser(host=host, port=port, password=password))
	ui.tableView.setModel(model)

def displayAbout():
	global ui
	title = "Futaam"
	aboutText = """A free and open source anime manager.
https://github.com/HarHar/Futaam"""
	QtGui.QMessageBox.about(ui.centralwidget, title, aboutText)

def main(argv):
	global model
	global ui
	global dbs
	global dbfile
	global port
	global host

	ircn = False
	i = 0
	for x in argv:
		if os.path.exists(x):
			dbfile.append(x)
		elif x == '--host':
			if len(argv) <= i:
				print colors.fail + 'Missing host' + colors.default
				sys.exit(1)
			elif argv[i+1].startswith('--'):
				print colors.fail + 'Missing host' + colors.default
				sys.exit(1)	
			else:
				host = argv[i+1]
		elif x == '--port':
			if len(argv) <= i:
				print colors.fail + 'Missing port' + colors.default
				sys.exit(1)
			elif argv[i+1].startswith('--') or argv[i+1].isdigit() == False:
				print colors.fail + 'Missing port' + colors.default
				sys.exit(1)	
			else:
				port = int(argv[i+1])
		elif x == '--password':
			if len(argv) <= i:
				print colors.fail + 'Missing password' + colors.default
				sys.exit(1)
			elif argv[i+1].startswith('--'):
				print colors.fail + 'Missing password' + colors.default
				sys.exit(1)	
			else:
				password = argv[i+1]
		elif x == '--ircnotify':
			ircn = True
		i += 1	

	if len(dbfile) == 0 and host == '':
		print colors.fail + 'No database file specified' + colors.default
		sys.exit(1)

	if host == '':
		dbs = []
		for fn in dbfile:
			dbs.append(parser.Parser(fn, ircHook=ircn))
		currentdb = 0
	else:
		if password == '':
			print colors.fail + 'Missing password! ' + colors.default + 'Use "--password [pass]"'
			sys.exit(1)
		dbs = []
		dbs.append(parser.Parser(host=host, port=port, password=password))
		currentdb = 0	

	app = QtGui.QApplication(argv)
	ui = uic.loadUi("./interfaces/ui/gui.ui")
	ui.show()

	model = TableModel()
	if len(argv) == 0:
		help()
	if len(dbfile) == 0 and len(dbs) > 0:
		dbfile = ['']
	model.load_db(dbfile[0], dbs[0])
	ui.tableView.setModel(model)

	QtCore.QObject.connect(ui.actionQuit, QtCore.SIGNAL("triggered()"), ui.close)
	QtCore.QObject.connect(ui.actionOpen, QtCore.SIGNAL("triggered()"), openFile)
	QtCore.QObject.connect(ui.actionSave, QtCore.SIGNAL("triggered()"), model.db.save)
	QtCore.QObject.connect(ui.actionDelete_Entry, QtCore.SIGNAL("triggered()"), deleteEntry)
	QtCore.QObject.connect(ui.actionAdd_Entry, QtCore.SIGNAL("triggered()"), addEntry)
	QtCore.QObject.connect(ui.actionSwap_Entries, QtCore.SIGNAL("triggered()"), swapEntries)
	QtCore.QObject.connect(ui.actionAbout_Futaam, QtCore.SIGNAL("triggered()"), displayAbout)
	QtCore.QObject.connect(ui.actionEdit_Entry, QtCore.SIGNAL("triggered()"), editEntry)

	exit(app.exec_())

def help():
	print """USAGE: ./futaam.py --gui [DATABASE]"""
	quit()

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
import sys
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
		self.headers = ["Title","Genres","Status","Watched","Observations"]
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

	def rebuildIds(self):
		for x in xrange(0, self.db.dictionary['count']):
			self.db.dictionary['items'][x]['id'] = x
		self.db.save()


class AddEntryDialog(QtGui.QDialog):
	def __init__(self, parent = None):
		QtGui.QDialog.__init__(self, parent)
		self.setWindowTitle("Add Entry")
		self.ui = uic.loadUi("./interfaces/ui/addDialog.ui", self)
		self.ui.show()
		
		self.ui.statusSelect.addItems(["Watched", "Queued", "Dropped", "Watching", "On Hold"])
		QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.add)
		QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("rejected()"), self.close)
		QtCore.QObject.connect(self.ui.titleLine, QtCore.SIGNAL("editingFinished()"), self.populateCB)
		QtCore.QObject.connect(self.ui.animeButton, QtCore.SIGNAL("toggled()"), self.populateCB)
		QtCore.QObject.connect(self.ui.resultSelect, QtCore.SIGNAL("currentIndexChanged(int)"), self.resultChanged)

	def populateCB(self):
		self.resultSelect.clear()
		title = self.ui.titleLine.text()
		if self.ui.animeButton.isChecked():
			search_results = utils.MALWrapper.search(title, "anime")
		else:
			search_results = utils.MALWrapper.search(title, "manga")
		for result in search_results:
			self.resultSelect.addItem(str(result["title"]))
		self.results = search_results

	def resultChanged(self, index):
		title = self.ui.titleLine.text()
		if self.ui.animeButton.isChecked():
			entryId = utils.MALWrapper.search(title, "anime")[index]['id']
			self.result = utils.MALWrapper.details(entryId, "anime")
		else:
			entryId = utils.MALWrapper.search(title, "manga")[index]
			self.result = utils.MALWrapper.details(entryId, "manga")
		genres = ""
		for genre in self.result['genres']:
			genres = genres + genre + '/'
		self.ui.genreLine.setText(genres[:-1])
		if self.ui.animeButton.isChecked():
			number = self.result['episodes']
		else:
			number = self.result['chapters']
		self.ui.episodesBox.setValue(number)

	def add(self):
		result = self.results[self.ui.resultSelect.currentIndex()]
		obs = self.ui.obsLine.text()
		statusIndex = self.ui.statusSelect.currentIndex()
		genres = self.ui.genreLine.text()
		if statusIndex == 0:
			if self.ui.animeButton.isChecked():
				eps = result['episodes']
				am = "anime"
			else:
				eps = result['chapters']
				am = "manga"
		else:
			eps = episodesBox.values()
			am = "anime"
		doAdd(result, obs, statusIndex, eps, genres, am)
		self.done(0)

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

class EntryInfoDialog(QtGui.QDialog):
	def __init__(self, parent=None, names=None, entries=None):
		QtGui.QDialog.__init__(self, parent)
		self.entries = entries
		self.ui = uic.loadUi("./interfaces/ui/infoDialog.ui", self)
		self.ui.show()

		self.ui.entrySelect.addItems(names)
		QtCore.QObject.connect(self.ui.closeButton, QtCore.SIGNAL("clicked()"), self.removeTempAndClose)
		QtCore.QObject.connect(self.ui.entrySelect, QtCore.SIGNAL("currentIndexChanged(int)"), self.fillEntries)
		self.fillEntries()

	def removeTempAndClose(self):
		try:
			os.remove(".temp")
		except:
			pass
		self.done(0)

	def fillEntries(self, index=0):
		self.index = index
		self.currentEntry = self.entries[self.index]
		details = MALWrapper.details(self.currentEntry['aid'], self.currentEntry['type'])

		self.ui.episodeLine.setText(str(details['episodes']))
		genres = ""
		for genre in details['genres']:
			genres = genres + genre + '/'
		self.ui.genreLine.setText(genres[:-1])
		self.ui.statusLine.setText(details['status'].title())
		self.ui.malRank.setText(str(details['rank']))
		self.ui.summaryText.setPlainText(utils.remove_html_tags(details['synopsis']))
		self.ui.dateLine.setText(details['start_date'][:10])
		self.ui.endDate.setText(details['end_date'][:10])
		if details['type'] == u'Movie':
			self.ui.typeLine.setText("Feature Film")
		elif details['type'] == u'TV':
			self.ui.typeLine.setText("TV Series")
		else:
			self.ui.typeLine.setText(details['type'])
		self.ui.pictureLabel.setText("")
		if os.path.exists(".temp"):
			os.remove(".temp")
		x=open(".temp", "w")
		x.write(urllib2.urlopen(details['image_url']).read())
		x.close()
		self.ui.pictureLabel.setText("<img src='.temp' width='175' height='223' align='right' />")

class aboutDialog(QtGui.QDialog):
	def __init__(self, parent=None):
		QtGui.QDialog.__init__(self, parent)
		self.ui = uic.loadUi("./interfaces/ui/aboutDialog.ui", self)
		self.ui.show()
		QtCore.QObject.connect(self.ui.closeButton, QtCore.SIGNAL("clicked()"), self.close)

class NewDbDialog(QtGui.QDialog):
	def __init__(self, parent=None):
		QtGui.QDialog.__init__(self, parent)
		self.ui = uic.loadUi("./interfaces/ui/newDbDialog.ui", self)
		self.ui.show()
		QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.makeNew)
		QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("rejected()"), self.close)
		QtCore.QObject.connect(self.ui.pathSelectButton, QtCore.SIGNAL("clicked()"), self.fileDialog)
		
	def fileDialog(self):
		filename = QtGui.QFileDialog.getSaveFileName(parent=self, filter="Futaam Database (*.db);; All Files (*)")
		self.ui.pathEdit.setText(filename)

	def makeNew(self):
		path = self.ui.pathEdit.text()
		if self.ui.jsonButton.isChecked():
			dbType = "json"
		else:
			dbType = "pickle"
		title = self.ui.nameLineEdit.text()
		des = self.ui.descriptionLineEdit.text()
		parser.createDB(str(path), str(dbType), str(title), str(des))
		self.close()

class DbStatsDialog(QtGui.QDialog):
	def __init__(self, parent=None):
		QtGui.QDialog.__init__(self, parent)
		self.ui = uic.loadUi("./interfaces/ui/statsDialog.ui", self)
		self.ui.show()

		self.ui.dbNameLabel.setText(model.db.dictionary["name"])
		self.ui.dbDescriptionLabel.setText(model.db.dictionary["description"])
		self.ui.entryNumLabel.setText(str(model.db.dictionary["count"]))
		numW = 0
		numQ = 0
		numH = 0
		numD = 0
		numC = 0
		for entry in model.db.dictionary["items"]:
			if entry["status"] == "w":
				numW = numW + 1
			elif entry["status"] == "q":
				numQ = numQ + 1
			elif entry["status"] == "d":
				numD = numD + 1
			elif entry["status"] == "h":
				numH = numH + 1
			elif entry["status"] == "c":
				numC = numC + 1
		self.ui.numWatchedLabel.setText(str(numW))
		self.ui.numDroppedLabel.setText(str(numD))
		self.ui.numQueuedLabel.setText(str(numQ))
		self.ui.numOnHoldLabel.setText(str(numH))
		self.ui.numCompletedLabel.setText(str(numC))

		QtCore.QObject.connect(self.ui.closeButton, QtCore.SIGNAL("clicked()"), self.close)

def showOpenDbDialog():
	global model
	filename = QtGui.QFileDialog.getOpenFileName(None, "Open Data File", "", "Futaam Database (*.db);; All Files (*)")
	if filename != None:
		model = TableModel()
		model.load_db(filename, parser.Parser(filename))
		ui.tableView.setModel(model)

def showDeleteEntryDialog():
	dialog = DeleteEntryDialog(parent=ui.centralwidget, names=model.getAnimeNames())
	toDelete = dialog.exec_()

def showAddEntryDialog():
	dialog = AddEntryDialog(parent=ui.centralwidget)
	dialog.exec_()

def showAboutDialog():
	dialog = aboutDialog(parent=ui.centralwidget)
	dialog.exec_()

def showStatsDialog():
	dialog = DbStatsDialog(parent=ui.centralwidget)
	dialog.exec_()

def showSwapEntriesDialog():
	dialog = SwapEntryDialog(names=model.getAnimeNames(), parent=ui.centralwidget)
	dialog.exec_()

def showEditEntryDialog():
	dialog = EditEntryDialog(parent=ui.centralwidget, names=model.getAnimeNames(), entries=model.db.dictionary['items'])
	dialog.exec_()

def showInfoDialog():
	dialog = EntryInfoDialog(parent=ui.centralwidget, names=model.getAnimeNames(), entries=model.db.dictionary['items'])
	dialog.exec_()

def showNewDbDialog():
	dialog = NewDbDialog(parent=ui.centralwidget)
	dialog.exec_()

def doSwap(index1, index2):
	entry1 = model.db.dictionary['items'][index1]
	entry2 = model.db.dictionary['items'][index2]
	model.db.dictionary['items'][index1] = entry2
	model.db.dictionary['items'][index2] = entry1
	model.rebuildIds()
	reloadTable()
	model.db.save()

def doAdd(malInfo, obs, statusIndex, eps, genres, am):
	status = model.cbIndexToStatus(statusIndex)
	try:
		model.db.dictionary['count'] += 1
	except:
		model.db.dictionary['count'] = 1
	model.db.dictionary['items'].append({'id': model.db.dictionary['count'], 'type': am, 'aid': malInfo['id'], 'name': utils.HTMLEntitiesToUnicode(utils.remove_html_tags(malInfo['title'])), 'genre': str(genres), 'status': status, 'lastwatched': eps, 'obs': str(obs)})
	model.rebuildIds()
	reloadTable()

def doDelete(index):
	entry = model.db.dictionary['items'][index]
	model.db.dictionary['items'].remove(entry)
	model.db.dictionary['count'] -= 1
	model.rebuildIds()
	reloadTable()

def doEdit(index, title, obs, status, eps, genre):
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

def reloadTable():
	global model
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
	ui.tableView.resizeColumnsToContents()

def openReadme():
	QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/HarHar/Futaam#futaam"))

def main(argv):
	global model
	global ui
	global dbs
	global dbfile
	global port
	global host
	colors = utils.colors()
	colors.enable()

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
		help()
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
	reloadTable()

	QtCore.QObject.connect(ui.actionQuit, QtCore.SIGNAL("triggered()"), ui.close)
	QtCore.QObject.connect(ui.actionOpen, QtCore.SIGNAL("triggered()"), showOpenDbDialog)
	QtCore.QObject.connect(ui.actionSave, QtCore.SIGNAL("triggered()"), model.db.save)
	QtCore.QObject.connect(ui.actionDelete_Entry, QtCore.SIGNAL("triggered()"), showDeleteEntryDialog)
	QtCore.QObject.connect(ui.actionAdd_Entry, QtCore.SIGNAL("triggered()"), showAddEntryDialog)
	QtCore.QObject.connect(ui.actionSwap_Entries, QtCore.SIGNAL("triggered()"), showSwapEntriesDialog)
	QtCore.QObject.connect(ui.actionAbout_Futaam, QtCore.SIGNAL("triggered()"), showAboutDialog)
	QtCore.QObject.connect(ui.actionEdit_Entry, QtCore.SIGNAL("triggered()"), showEditEntryDialog)
	QtCore.QObject.connect(ui.actionViewDetails, QtCore.SIGNAL("triggered()"), showInfoDialog)
	QtCore.QObject.connect(ui.actionNew, QtCore.SIGNAL("triggered()"), showNewDbDialog)
	QtCore.QObject.connect(ui.actionStats, QtCore.SIGNAL("triggered()"), showStatsDialog)
	QtCore.QObject.connect(ui.actionReadme, QtCore.SIGNAL("triggered()"), openReadme)

	exit(app.exec_())

def help():
	print """USAGE: ./futaam.py --gui [DATABASE] [Qt Options]"""
	quit()

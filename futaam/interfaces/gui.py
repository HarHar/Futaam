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
import os
import sys
import urllib2
import inspect
import getpass
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic
from futaam.interfaces import ARGS
from futaam.interfaces.common import parser
from futaam.interfaces.common import utils
DB_FILE = []
HOST = ''
PORT = 8500
DBS = []
PASSWORD = ''
USERNAME = ''
HOOKS = []

def cur_dir():
    return os.path.dirname(inspect.getsourcefile(cur_dir)) + os.path.sep

class TableModel(QtCore.QAbstractTableModel):
    """This class implements QAbstractTableModel in order to create
    a table that can hold a futaam db's information"""
    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.anime_list = []
        self.headers = ["Title", "Genres", "Status", "Watched", "Observations"]
        self.active_file = ""

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 5

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid() == False:
            return QtCore.QVariant()
        if index.row() >= self.rowCount() or index.row() < 0:
            return QtCore.QVariant()

        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return self.anime_list[index.row()][0]
            elif index.column() == 1:
                return self.anime_list[index.row()][1]
            elif index.column() == 2:
                return self.anime_list[index.row()][2]
            elif index.column() == 3:
                return self.anime_list[index.row()][3]
            elif index.column() == 4:
                return self.anime_list[index.row()][4]

        return QtCore.QVariant()

    def get_entry_names(self):
        names = []
        for anime in self.anime_list:
            names.append(anime[0])
        return names

    def headerData(self, column, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role ==\
		QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.headers[column])
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(" ")
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.anime_list)

    def load_db(self, fl, db):
        self.active_file = fl
        self.db = db
        for entry in self.db.dictionary['items']:
            self.anime_list.append([entry["name"], entry["genre"], 
			utils.translated_status[entry['type'].lower()][
            entry["status"].lower()],
			entry["lastwatched"], entry["obs"]])

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

    def addEntry(self, malInfo, obs, statusIndex, eps, genres, am):
        status = self.cbIndexToStatus(statusIndex)
        try:
            self.db.dictionary['count'] += 1
        except:
            self.db.dictionary['count'] = 1
        title = utils.HTMLEntitiesToUnicode(
            utils.remove_html_tags(malInfo['title']))
        title = title.replace("&amp;", "&")
        self.db.dictionary['items'].append({'id': self.db.dictionary['count'],
        'type': am, 'aid': malInfo['id'], 'name': title, 'genre': str(genres),
        'status': status, 'lastwatched': eps, 'obs': str(obs)})
        self.rebuildIds()
        reloadTable()

    def deleteEntry(self, index):
        entry = self.db.dictionary['items'][index]
        self.db.dictionary['items'].remove(entry)
        self.db.dictionary['count'] -= 1
        self.rebuildIds()
        reloadTable()

    def editEntry(self, index, title, obs, status, eps, genre):
        entry = self.db.dictionary['items'][index]
        # NOTE: The string we've gotten back from Qt
        # functions are QStrings and need to be converted
        # back into regular ones before we can save them
        entry['name'] = unicode(title)
        entry['obs'] = str(obs)
        entry['lastwatched'] = str(eps)
        entry['status'] = model.cbIndexToStatus(status)
        entry['genre'] = str(genre)
        self.db.save()
        reloadTable()

    def swapEntries(self, index1, index2):
        entry1 = self.db.dictionary['items'][index1]
        entry2 = self.db.dictionary['items'][index2]
        self.db.dictionary['items'][index1] = entry2
        self.db.dictionary['items'][index2] = entry1
        self.rebuildIds()
        self.db.save()
        reloadTable()


class AddEntryDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("Add Entry")
        self.ui = uic.loadUi(uiPrefix + "addDialog.ui", self)
        self.ui.show()

        self.ui.statusSelect.addItems(
            ["Watched", "Queued", "Dropped", "Watching", "On Hold"])
        QtCore.QObject.connect(
            self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.add)
        QtCore.QObject.connect(
            self.ui.buttonBox, QtCore.SIGNAL("rejected()"), self.close)
        QtCore.QObject.connect(
            self.ui.titleLine, QtCore.SIGNAL("editingFinished()"), 
            self.populateCB)
        QtCore.QObject.connect(
            self.ui.animeButton, QtCore.SIGNAL("toggled(bool)"), 
            self.populateCB)
        QtCore.QObject.connect(
            self.ui.animeButton, QtCore.SIGNAL("toggled(bool)"),
            self.populateCB)
        QtCore.QObject.connect(self.ui.resultSelect, QtCore.SIGNAL(
            "currentIndexChanged(int)"), self.resultChanged)

    def populateCB(self):
        self.resultSelect.clear()
        title = self.ui.titleLine.text()
        if title == "":
            return
        if self.ui.animeButton.isChecked():
            search_results = ANN.search(str(title), "anime", True)
        elif self.ui.mangaButton.isChecked():
            search_results = ANN.search(str(title), "manga", True)
        elif self.ui.vnButton.isChecked():
            self.vndb = utils.VNDB("Futaam", "0.1")
            search_results = self.vndb.get(
                'vn', 'basic', '(title~"' + title + '")', '')['items']
            self.vndb.close()
        else:
            search_results = []
        for result in search_results:
            self.resultSelect.addItem(unicode(result["title"]))
        self.results = search_results

    def resultChanged(self, index):
        title = self.ui.titleLine.text()
        if self.ui.animeButton.isChecked():
            entryId = ANN.search(str(title), "anime", True)[index]['id']
            self.result = ANN.details(entryId, "anime")
        elif self.ui.animeButton.isChecked():
            entryId = ANN.search(str(title), "manga", True)[index]['id']
            self.result = ANN.details(entryId, "manga")
        # VNDB doesn't have genre info and epsidoes
        # are a silly concept for VNs
        else:
            self.ui.genreLine.setText("")
            self.ui.episodesBox.setValue(0)
            return
        genres = ""
        for genre in self.result['genres']:
            genres = genres + genre + '/'
        self.ui.genreLine.setText(genres[:-1])
        if self.ui.animeButton.isChecked():
            number = self.result['episodes']
            # the following condition will only be true if the entry is a
            # movie so we can safely set episodes to 1
            if number == None:
                number = 1
        elif self.ui.mangaButton.isChecked():
            number = self.result['chapters']
        else:
            number = 0
        self.ui.episodesBox.setValue(number)

    def add(self):
        result = self.result
        obs = self.ui.obsLine.text()
        statusIndex = self.ui.statusSelect.currentIndex()
        genres = self.ui.genreLine.text()
        if self.ui.animeButton.isChecked():
            am = "anime"
        elif self.ui.mangaButton.isChecked():
            am = "manga"
        else:
            am = "vn"

        if statusIndex == 0:
            if self.ui.animeButton.isChecked():
                eps = result['episodes']	
                # the following condition will only be true if the entry is a
                # movie so we can safely set episodes to 1
                if eps == None:
                    eps = 1
            elif self.ui.mangaButton.isChecked():
                eps = result['chapters']
            else:
                eps = 1
        else:
            eps = self.ui.episodesBox.value()
        model.addEntry(result, obs, statusIndex, eps, genres, am)
        self.done(0)


class DeleteEntryDialog(QtGui.QDialog):

    def __init__(self, parent=None, names=[], index=0):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi(uiPrefix + "deleteDialog.ui", self)
        self.ui.show()

        self.selectBox.addItems(names)
        self.selectBox.setCurrentIndex(index)
        QtCore.QObject.connect(
            self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.delete)
        QtCore.QObject.connect(
            self.ui.buttonBox, QtCore.SIGNAL("rejected()"), self.close)

    def delete(self):
        model.deleteEntry(self.ui.selectBox.currentIndex())
        self.done(0)


class SwapEntryDialog(QtGui.QDialog):

    def __init__(self, parent=None, names=[]):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi(uiPrefix + "swapDialog.ui", self)
        self.ui.show()

        self.ui.selectBox1.addItems(names)
        self.ui.selectBox2.addItems(names)
        QtCore.QObject.connect(
            self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.swap)
        QtCore.QObject.connect(
            self.ui.buttonBox, QtCore.SIGNAL("rejected()"), self.close)

    def swap(self):
        entry1 = self.selectBox1.currentIndex()
        entry2 = self.selectBox2.currentIndex()
        if entry1 == entry2:
            self.done(0)
        model.swapEntries(entry1, entry2)
        self.done(0)


class EditEntryDialog(QtGui.QDialog):

    def __init__(self, parent=None, names=None, entries=None, index=0):
        QtGui.QDialog.__init__(self, parent)
        self.entries = entries
        self.ui = uic.loadUi(uiPrefix + "editDialog.ui", self)
        self.ui.show()

        self.ui.entrySelect.addItems(names)
        self.ui.entrySelect.setCurrentIndex(index)
        self.ui.statusSelect.addItems(
            ["Watched", "Queued", "Dropped", "Watching", "On Hold"])
        QtCore.QObject.connect(
            self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.edit)
        QtCore.QObject.connect(
            self.ui.buttonBox, QtCore.SIGNAL("rejected()"), self.close)
        QtCore.QObject.connect(self.ui.entrySelect, QtCore.SIGNAL(
            "currentIndexChanged(int)"), self.fillEntries)
        self.fillEntries(index)

    def fillEntries(self, index=0):
        self.index = index
        self.currentEntry = self.entries[self.index]
        self.ui.titleLine.setText(self.currentEntry['name'])
        self.ui.obsLine.setText(self.currentEntry['obs'])
        self.ui.episodesSelect.setValue(int(self.currentEntry['lastwatched']))
        self.ui.genreLine.setText(self.currentEntry['genre'])

    def edit(self):
        model.editEntry(
            self.index, self.ui.titleLine.text(), self.ui.obsLine.text(),
            self.ui.statusSelect.currentIndex(
            ), self.ui.episodesSelect.value(),
            self.ui.genreLine.text())


class EntryInfoDialog(QtGui.QDialog):

    def __init__(self, parent=None, names=None, entries=None, index=0):
        QtGui.QDialog.__init__(self, parent)
        self.entries = entries
        self.ui = uic.loadUi(uiPrefix + "infoDialog.ui", self)
        self.ui.show()
        self.showingVN = False

        self.ui.entrySelect.addItems(names)
        self.ui.entrySelect.setCurrentIndex(index)
        QtCore.QObject.connect(
            self.ui.closeButton, QtCore.SIGNAL("clicked()"), 
            self.removeTempAndClose)
        QtCore.QObject.connect(self.ui.entrySelect, QtCore.SIGNAL(
            "currentIndexChanged(int)"), self.fillEntries)
        self.fillEntries(index)

    def removeTempAndClose(self):
        try:
            os.remove(".temp")
        except:
            pass
        self.done(0)

    def fillEntries(self, index=0):
        self.index = index
        self.currentEntry = self.entries[self.index]
        if self.currentEntry["type"] != "vn":
            details = ANN.details(
                self.currentEntry['aid'], self.currentEntry['type'])
            self.showingVN = False
        else:
            vndb = utils.VNDB("Futaam", "0.1")
            details = vndb.get("vn", "basic,details", "(id = " +\
            str(self.currentEntry['aid']) + ")", "")["items"][0]
            vndb.close()
            self.showingVN = True
            self.ui.releaseDateLine.setText(details["released"])
            self.ui.platformsLine.setText(", ".join(details["platforms"]))
        self.toggleVnFields()

        if self.currentEntry['type'] != 'vn':
            self.ui.episodeLine.setText(str(details['episodes']))
            genres = ""
            for genre in details['genres']:
                genres = genres + genre + '/'
            self.ui.genreLine.setText(genres[:-1])
        syn_key = 'synopsis' if self.currentEntry[
            'type'] != 'vn' else 'description'
        self.ui.summaryText.setPlainText(utils.HTMLEntitiesToUnicode(
            utils.remove_html_tags(details[syn_key])))
        date = details['start_date'][:10] if self.currentEntry[
            'type'] != 'vn' else details['released']
        # self.ui.dateLine.setText()

        if self.currentEntry['type'] == 'vn':
            self.ui.typeLine.setText("Visual Novel")
        #else:
        #    if len(details['prequels']) == 0:
        #        self.ui.parentStoryLine.setText("None")
        #    else:
        #        self.ui.parentStoryLine.setText(
        #            details['prequels'][0]['title'])
        #    if details['end_date'] == None:
        #        self.ui.endDate.setText("Unknown")
        #    else:
        #        self.ui.endDate.setText(details['end_date'][:10])
        #    if details['type'] == u'Movie':
        #        self.ui.typeLine.setText("Feature Film")
        #    elif details['type'] == u'TV':
        #        self.ui.typeLine.setText("TV Series")
        #    else:
        #        self.ui.typeLine.setText(details['type'])

        self.ui.pictureLabel.setText("")
        if os.path.exists(".temp"):
            os.remove(".temp")
        x = open(".temp", "w")
        img_key = '_url' if self.currentEntry['type'] != 'vn' else ''
        x.write(urllib2.urlopen(details['image' + img_key]).read())
        x.close()
        self.ui.pictureLabel.setText(
            "<img src='.temp' width='225' height='350' align='right' />")
        self.ui.pictureLabel.setScaledContents(True)

    def toggleVnFields(self):
        if self.showingVN == True:
            # turn off anime/manga fields
            self.ui.label_11.hide()
            self.ui.parentStoryLine.hide()
            self.ui.label_3.hide()
            self.ui.malRank.hide()
            self.ui.genreLine.hide()
            self.ui.label_6.hide()
            self.ui.label_7.hide()
            self.ui.dateLine.hide()
            self.ui.label_9.hide()
            self.ui.endDate.hide()
            self.ui.label_5.hide()
            self.ui.statusLine.hide()
            self.ui.label_4.hide()
            self.ui.episodeLine.hide()
            # show VN fields
            self.ui.label_14.show()
            self.ui.platformsLine.show()
            self.ui.label_10.show()
            self.ui.releaseDateLine.show()
        else:
            # show anime/manga fields
            self.ui.label_11.show()
            self.ui.parentStoryLine.show()
            self.ui.label_3.show()
            self.ui.malRank.show()
            self.ui.genreLine.show()
            self.ui.label_6.show()
            self.ui.label_7.hide()
            self.ui.dateLine.show()
            self.ui.label_9.show()
            self.ui.endDate.show()
            self.ui.label_5.show()
            self.ui.statusLine.show()
            self.ui.label_4.show()
            self.ui.episodeLine.show()
            # hide VN fields
            self.ui.label_14.hide()
            self.ui.platformsLine.hide()
            self.ui.label_10.hide()
            self.releaseDateLine.hide()


class aboutDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi(uiPrefix + "aboutDialog.ui", self)
        self.ui.show()
        QtCore.QObject.connect(
            self.ui.closeButton, QtCore.SIGNAL("clicked()"), self.close)


class NewDbDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi(uiPrefix + "newDbDialog.ui", self)
        self.ui.show()
        QtCore.QObject.connect(
            self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.makeNew)
        QtCore.QObject.connect(
            self.ui.buttonBox, QtCore.SIGNAL("rejected()"), self.close)
        QtCore.QObject.connect(
            self.ui.pathSelectButton, QtCore.SIGNAL("clicked()"), 
			self.fileDialog)

    def fileDialog(self):
        filename = QtGui.QFileDialog.getSaveFileName(
            parent=self, filter="Futaam Database (*.db);; All Files (*)")
        self.ui.pathEdit.setText(filename)

    def makeNew(self):
        path = self.ui.pathEdit.text()
        title = self.ui.nameLineEdit.text()
        des = self.ui.descriptionLineEdit.text()
        parser.createDB(str(path), "jso", str(title), str(des))
        self.close()


class DbStatsDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi(uiPrefix + "statsDialog.ui", self)
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

        QtCore.QObject.connect(
            self.ui.closeButton, QtCore.SIGNAL("clicked()"), self.close)


def showOpenDbDialog():
    global model
    filename = QtGui.QFileDialog.getOpenFileName(
        ui.centralwidget, "Open Data File", "", 
		"Futaam Database (*.db);; All Files (*)")
    if filename != None:
        model = TableModel()
        model.load_db(filename, parser.Parser(filename))
        ui.tableView.setModel(model)


def showDeleteEntryDialog():
    dialog = DeleteEntryDialog(
        parent=ui.centralwidget, names=model.get_entry_names())
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
    dialog = SwapEntryDialog(
        names=model.get_entry_names(), parent=ui.centralwidget)
    dialog.exec_()


def showEditEntryDialog():
    dialog = EditEntryDialog(
        parent=ui.centralwidget, names=model.get_entry_names(), 
		entries=model.db.dictionary['items'])
    dialog.exec_()


def showInfoDialog():
    dialog = EntryInfoDialog(
        parent=ui.centralwidget, names=model.get_entry_names(), 
		entries=model.db.dictionary['items'])
    dialog.exec_()


def showInfoDialog_preselected(index):
    dialog = EntryInfoDialog(
        parent=ui.centralwidget, names=model.get_entry_names(),
        entries=model.db.dictionary['items'], index=index.row())
    dialog.exec_()


def showNewDbDialog():
    dialog = NewDbDialog(parent=ui.centralwidget)
    dialog.exec_()


def reloadTable():
    global model
    filename = model.active_file
    model = TableModel(parent=ui.centralwidget)
    if HOST == '':
        model.load_db(filename, parser.Parser(DB_FILE[0]))
    else:
        if PASSWORD == '':
            print colors.fail + 'Missing password! ' + colors.default +\
			'Use "--password [pass]"'
            sys.exit(1)
        model.load_db(filename, parser.Parser(
            HOST, PORT, PASSWORD))
    ui.tableView.setModel(model)
    ui.tableView.resizeColumnsToContents()
    ui.tableView.verticalHeader().setResizeMode(
        QtGui.QHeaderView.ResizeToContents)


def openReadme():
    QtGui.QDesktopServices.openUrl(
        QtCore.QUrl("https://github.com/HarHar/Futaam#futaam"))


def dragSwap(logicalIndex, originalIndex, newIndex):
    model.swapEntries(logicalIndex, newIndex)


def table_menu(position):
    menu = QtGui.QMenu()
    infoAction = menu.addAction("Info")
    editAction = menu.addAction("Edit")
    deleteAction = menu.addAction("Delete")
    incrementAction = menu.addAction("Increment Progress")

    action = menu.exec_(ui.tableView.mapToGlobal(position))
    if action == infoAction:
        dialog = EntryInfoDialog(
            parent=ui.centralwidget, names=model.get_entry_names(),
            entries=model.db.dictionary['items'], 
			index=ui.tableView.indexAt(position).row())
        dialog.exec_()
    elif action == editAction:
        dialog = EditEntryDialog(
            parent=ui.centralwidget, names=model.get_entry_names(),
            entries=model.db.dictionary['items'], 
			index=ui.tableView.indexAt(position).row())
        dialog.exec_()
    elif action == deleteAction:
        model.deleteEntry(ui.tableView.indexAt(position).row())
    elif action == incrementAction:
        index = ui.tableView.indexAt(position).row()
        entry = model.db.dictionary['items'][index]
        newEps = unicode(int(entry['lastwatched']) + 1)
        model.editEntry(
            index, entry['name'], entry['obs'], 3, newEps, entry['genre'])


def main(argv, version):
    global model
    global ui
    global uiPrefix
    global ANN
    global DB_FILE
    global DBS
    global USERNAME
    global PASSWORD
    global PORT 
    global HOST
    global HOOKS

    ANN = utils.ANNWrapper()
    ANN.init()

    confpath = os.path.join(
        os.getenv('USERPROFILE') or os.getenv('HOME'), '.futaam')
    if os.path.exists(confpath):
        f = open(confpath, 'r')
        confs = json.load(f)
        f.close()
    else:
        confs = {}

    colors = utils.colors()
    colors.enable()

    uiPrefix = None
    if os.name == "nt":
        if os.path.exists(sys.prefix + "\\Scripts\\futaam"):
            uiPrefix = sys.prefix + "\\Scripts\\futaam\\"
    else:
        if os.path.exists("/usr/share/futaam/"):
            uiPrefix = "/usr/share/futaam/"
        elif os.path.exists("/usr/local/share/futaam"):
            uiPrefix = "/usr/local/share/futaam/"
    if uiPrefix == None:
        uiPrefix = cur_dir() + "/ui/"

    app = QtGui.QApplication(argv)

    for x in argv:
        if os.path.exists(x):
            break
    else:
        filename = QtGui.QFileDialog.getOpenFileName(
            None, "Open Data File", "", 
            "Futaam Database (*.db);; All Files (*)")
        if filename != None:
            argv.append(filename)

    # gather arguments
    DB_FILE = ARGS.database
    if ARGS.host:
       HOST = ARGS.host
    if ARGS.password:
       PASSWORD = ARGS.password
    if ARGS.username:
        USERNAME = ARGS.username
    if ARGS.port:
        PORT = ARGS.port
    if ARGS.hooks:
        HOOKS = ARGS.hooks

    if len(DB_FILE) == 0 and HOST == '':
        print colors.fail + 'No database file specified' + colors.default
        help()
        sys.exit(1)
    if HOST == '':
        DBS = []
        for fn in DB_FILE:
            DBS.append(parser.Parser(fn, hooks=HOOKS))
        currentdb = 0
    else:
        if USERNAME == '':
            if 'default.user' in confs:
                print '[' + colors.blue + 'info' + colors.default +\
                '] using default user'
                USERNAME = confs['default.user']
            else:
                USERNAME = raw_input('Username for \'' + HOST + '\': ')
        if 'default.password' in confs:
            print '[' + colors.blue + 'info' + colors.default +\
            '] using default password'
            PASSWORD = confs['default.password']
        else:
            PASSWORD = getpass.getpass(
                'Password for ' + USERNAME + '@' + HOST + ': ')
        DBS = []
        try:
            DBS.append(
                parser.Parser(HOST=host, PORT=port, username=USERNAME, 
                password=password, hooks=HOOKS))
        except Exception, e:
            print '[' + colors.fail + 'error' + colors.default + '] ' +\
            str(e).replace('305 ', '')
            sys.exit(1)
        currentdb = 0

    ui = uic.loadUi(uiPrefix + "gui.ui")
    ui.show()

    model = TableModel(parent=ui.centralwidget)
    if len(argv) == 0:
        help()
    if len(DB_FILE) == 0 and len(DBS) > 0:
        DB_FILE = ['']
    model.load_db(DB_FILE[0], DBS[0])
    ui.tableView.setModel(model)
    rowHeader = ui.tableView.verticalHeader()
    rowHeader.setMovable(True)
    reloadTable()
    ui.tableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    ui.tableView.customContextMenuRequested.connect(table_menu)

    QtCore.QObject.connect(
        ui.actionQuit, QtCore.SIGNAL("triggered()"), ui.close)
    QtCore.QObject.connect(
        ui.actionOpen, QtCore.SIGNAL("triggered()"), showOpenDbDialog)
    QtCore.QObject.connect(
        ui.actionSave, QtCore.SIGNAL("triggered()"), model.db.save)
    QtCore.QObject.connect(
        ui.actionDelete_Entry, QtCore.SIGNAL("triggered()"), 
        showDeleteEntryDialog)
    QtCore.QObject.connect(
        ui.actionAdd_Entry, QtCore.SIGNAL("triggered()"), showAddEntryDialog)
    QtCore.QObject.connect(
        ui.actionSwap_Entries, QtCore.SIGNAL("triggered()"), 
        showSwapEntriesDialog)
    QtCore.QObject.connect(
        ui.actionAbout_Futaam, QtCore.SIGNAL("triggered()"), showAboutDialog)
    QtCore.QObject.connect(
        ui.actionEdit_Entry, QtCore.SIGNAL("triggered()"), showEditEntryDialog)
    QtCore.QObject.connect(
        ui.actionViewDetails, QtCore.SIGNAL("triggered()"), showInfoDialog)
    QtCore.QObject.connect(
        ui.actionNew, QtCore.SIGNAL("triggered()"), showNewDbDialog)
    QtCore.QObject.connect(
        ui.actionStats, QtCore.SIGNAL("triggered()"), showStatsDialog)
    QtCore.QObject.connect(
        ui.actionReadme, QtCore.SIGNAL("triggered()"), openReadme)
    QtCore.QObject.connect(ui.tableView, QtCore.SIGNAL(
        "doubleClicked(QModelIndex)"), showInfoDialog_preselected)
    QtCore.QObject.connect(
        rowHeader, QtCore.SIGNAL("sectionMoved(int, int, int)"), dragSwap)
    exit(app.exec_())


def print_help():
    print """USAGE: ./futaam.py --gui [DATABASE] [Qt Options]"""
    quit()

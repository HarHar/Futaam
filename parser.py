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
import pickle
import json
import os
from StringIO import StringIO

def createDB(filename, dbtype, name='', description='', items=[]):
	if dbtype in ['json', 'pickle'] == False:
		raise Exception('Wrong db type')

	if isinstance(items, list) == False: raise AssertionError
	for item in items: if isinstance(item, dict) == False: raise AssertionError

	f = open(filename, 'w')
	f.write('[' + dbtype + ']\n')
	tmp = {'name': name, 'description': description, 'items': items}
	if dbtype == 'pickle':
		f.write(pickle.dumps(tmp))
	elif dbtype == 'json':
		f.write(json.dumps(tmp))
	f.close()

class Parser(object):
	def __init__(self, filename, host='localhost', port=0):
		self.host = host
		self.port = port
		if os.path.exists(filename):
			if host == 'localhost':
				self.filename = filename
				f = open(filename, 'r')
				txt = f.read().replace('\r', '')
				lines = txt.split('\n')
				f.close()

			if len(lines) == 0:
				raise Exception('Empty file')

			if lines[0].lower() == '[json]':
				self.dbtype = 'json'
				self.dictionary = json.load(StringIO(txt[len('[json]\n'):]))
			elif lines[0].lower() == '[pickle]':
				self.dbtype = 'pickle'
				self.dictionary = pickle.loads(txt[len('[pickle]\n'):])
			else:
				raise Exception('Invalid database type')
		else:
			raise Exception('File does not exists')
	def save(self):
		if self.host == 'localhost':
			f = open(self.filename, 'w')
			f.write('[' + self.dbtype + ']\n')

			if self.dbtype == 'pickle':
				f.write(pickle.dumps(self.dictionary))
			elif self.dbtype == 'json':
				f.write(json.dumps(self.dictionary))

<<<<<<< HEAD
			f.close()
=======
		f.close()
>>>>>>> added License (GPL3) and worked a bit on setup.py

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
import json
import os
from StringIO import StringIO

class Parser(object):
	def __init__(self, filename):
		if os.path.exists(filename):
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
				self.dictionary = pickle.loads(txt[len('[pickle]\n':)])
			else:
				raise Exception('Invalid database type')
		else:
			raise Exception('File does not exists')
	def save(self):
		f = open(self.filename, 'w')
		f.write('[' + self.dbtype + ']\n')

		if self.dbtype == 'pickle':
			f.write(pickle.dumps(self.dictionary))
		elif self.dbtype == 'json':
			f.write(json.dumps(self.dictionary))

		f.close()
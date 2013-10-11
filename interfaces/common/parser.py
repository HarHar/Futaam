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
import json
import os
from StringIO import StringIO
import socket
from time import sleep
import hashlib
import time
import copy
from interfaces.common import utils

def createDB(filename, dbtype='json', name='', description='', items=[]):
	if dbtype in ['json'] == False:
		raise Exception('Wrong db type')

	if isinstance(items, list) == False: raise AssertionError
	for item in items:
		if isinstance(item, dict) == False: raise AssertionError

	f = open(os.path.expanduser(os.path.expandvars(filename)), 'w')
	f.write('[' + dbtype + ']\n')
	tmp = {'name': name, 'description': description, 'count': len(items), 'items': items}
	if dbtype == 'json':
		f.write(json.dumps(tmp))
	f.close()

class printHook(object):
	"""Example hook that prints the changes made"""
	def added(self, entry):
		print('[print hook] new entry added ({0})'.format(entry['name']))

	def removed(self, entry):
		print('[print hook] entry removed ({0})'.format(entry['name']))

	def propertyChanged(self, oldEntry, newEntry, propertyName):
		print('[print hook] "{0}" property changed on entry "{1}" ({2} -> {3})'.format(propertyName, newEntry['name'], oldEntry[propertyName], newEntry[propertyName]))

class IRCHook(object):
	"""Hook that announces the changes on the database on a IRC channel; note: you must first start the "irc" interface"""
	def __init__(self, port=5124):
		self.port = port
		self.statusColors = {'w': '3', 'd': '4', 'q': '6', 'c': '2', 'h': '7'}

	def msg(self, msg):
		sock = socket.socket()
		sock.connect(('localhost', self.port))
		sock.send(json.dumps({'action': 'msg', 'value': msg}))
		time.sleep(0.1)
		sock.close()

	def added(self, entry):
		self.msg('Added {0}{2}{3} ({1}{4}{3})'.format('\x02', '\x03' + self.statusColors[entry['status']], entry['name'], '\x15', utils.translated_status[entry['type']][entry['status'].lower()]))

	def removed(self, entry):
		self.msg('Removed {0}{1}'.format('\x02', entry['name']))

	def propertyChanged(self, oldEntry, newEntry, propertyName):
		if propertyName == 'obs':
			self.msg('[{0}] Observation: "{1}" --> "{2}"'.format(newEntry['name'], oldEntry[propertyName], newEntry[propertyName]))
		elif propertyName == 'status':
			self.msg('[{0}] {1} -> {2}'.format(newEntry['name'], '\x03' + self.statusColors[oldEntry['status']] + utils.translated_status[oldEntry['type']][oldEntry['status'].lower()] + '\x15', '\x03' + self.statusColors[newEntry['status']] + utils.translated_status[oldEntry['type']][newEntry['status'].lower()] + '\x15'))
		elif propertyName == 'lastwatched':
			action = 'Watched ' if newEntry['type'] == 'anime' else 'Read ' if newEntry['type'] == 'manga' else 'Played ' if newEntry['type'] == 'vn' else ''
			thing = 'episodes' if newEntry['type'] == 'anime' else 'chapters' if newEntry['type'] == 'manga' else ''
			if newEntry['lastwatched'].isdigit() and oldEntry['lastwatched'].isdigit():
				self.msg('[{0}] {1}from {2} to {3} ({4} {6} {5})'.format(newEntry['name'], action, oldEntry['lastwatched'], newEntry['lastwatched'], action.lower().strip(), thing, int(newEntry['lastwatched']) - int(oldEntry['lastwatched'])))
			else:
				self.msg('[{0}] {1}from {2} to {3}'.format(newEntry['name'], action, oldEntry['lastwatched'], newEntry['lastwatched']))

availableHooks = {'printHook': printHook, 'irc': IRCHook}

class Parser(object):
	def __init__(self, filename='', host='', port=8500, password='', username='', hooks=[]):
		self.host = host
		self.port = port
		self.password = password
		self.hooks = hooks
		for hook in self.hooks:
			hook.parser = self
		if host != '':
			self.sock = socket.socket()
			self.sock.connect((host, port))
			if password.startswith('sha256:'):
				self.sock.sendall(username + '/' + password.replace('sha256:', ''))
			else:
				self.sock.sendall(username + '/' + hashlib.sha256(password).hexdigest())
			rc = self.sock.recv(1024)
			if rc == 'OK':
				cmd = {'cmd': 'pull', 'args': ''}
				self.sock.sendall(json.dumps(cmd) + chr(4))

				rc = ''
				while rc[-1:] != chr(4):
					rc += self.sock.recv(4096)
				if json.load(StringIO(rc[:-1]))['response'].find('err:') == 0:
					print(json.load(StringIO(rc[:-1]))['response'].replace('err:', '').strip())
					exit(1)

				self.dictionary = json.load(StringIO(json.load(StringIO(rc[:-1]))['response']))
				return
			else:
				raise Exception(rc)
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
			else:
				raise Exception('Invalid database type')
		else:
			raise Exception('File does not exist')
		if len(self.hooks) != 0:
			self.tempdict = copy.deepcopy(self.dictionary)
	def hash(self):
		for entry in self.dictionary['items']:
			if entry.get('hash') == None:
				entry['hash'] = hashlib.sha256(entry['name'].encode('utf-8') + str(time.time())).hexdigest()
	def save(self):
		self.hash()
		if self.host == '':
			f = open(self.filename, 'w')
			f.write('[' + self.dbtype + ']\n')

			if self.dbtype == 'json':
				f.write(json.dumps(self.dictionary))
			f.close()
		else:
			self.sock.sendall(json.dumps({'cmd': 'push', 'args': json.dumps(self.dictionary)}) + chr(4)) #jsonception
			sleep(0.2)
			self.sock.sendall(json.dumps({'cmd': 'save'}) + chr(4))

		if len(self.hooks) != 0:
			keys = ['lastwatched', 'status', 'obs', 'name']

			hashesMatched = []
			for newEntry in self.dictionary['items']:
				for oldEntry in self.tempdict['items']:
					if newEntry['hash'] == oldEntry['hash']:
						hashesMatched.append(newEntry['hash'])
						for key in keys:
							if newEntry[key] != oldEntry[key]:
								for hook in self.hooks:
									hook.propertyChanged(oldEntry, newEntry, key)

			for entry in self.dictionary['items']:
				if (entry['hash'] in hashesMatched) == False:
					for hook in self.hooks:
						hook.added(entry)

			for entry in self.tempdict['items']:
				if (entry['hash'] in hashesMatched) == False:
					for hook in self.hooks:
						hook.removed(entry)
		self.tempdict = copy.deepcopy(self.dictionary)
	def reload(self):
		if self.host != '': self.sock.close()
		self.__init__(self.filename, self.host, self.port, self.password)
	def rNext(self):
		if self.host != '':
			self.sock.send(json.dumps({'cmd': 'sdb', 'args': ''}) + chr(4))
			sleep(1)
			cmd = {'cmd': 'pull', 'args': ''}
			self.sock.sendall(json.dumps(cmd) + chr(4))
			rc = ''
			while rc[-1:] != chr(4):
				rc += self.sock.recv(4096)
			self.dictionary = json.load(StringIO(json.load(StringIO(rc[:-1]))['response']))


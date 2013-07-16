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
import socket
from time import sleep
import hashlib
import time
import copy
from interfaces.common import utils

class SafeUnpickler(pickle.Unpickler):
    PICKLE_SAFE = {
        'copy_reg': set(['_reconstructor']),
        '__builtin__': set(['object'])
    }
    def find_class(self, module, name):
        if not module in self.PICKLE_SAFE:
            raise pickle.UnpicklingError(
                'Attempting to unpickle unsafe module %s' % module
            )
        __import__(module)
        mod = sys.modules[module]
        if not name in self.PICKLE_SAFE[module]:
            raise pickle.UnpicklingError(
                'Attempting to unpickle unsafe class %s' % name
            )
        klass = getattr(mod, name)
        return klass
    @classmethod
    def loads(cls, pickle_string):
        return cls(StringIO(pickle_string)).load()

def createDB(filename, dbtype, name='', description='', items=[]):
	if dbtype in ['json', 'pickle'] == False:
		raise Exception('Wrong db type')

	if isinstance(items, list) == False: raise AssertionError
	for item in items:
		if isinstance(item, dict) == False: raise AssertionError

	f = open(filename, 'w')
	f.write('[' + dbtype + ']\n')
	tmp = {'name': name, 'description': description, 'count': len(items), 'items': items}
	if dbtype == 'pickle':
		f.write(pickle.dumps(tmp))
	elif dbtype == 'json':
		f.write(json.dumps(tmp))
	f.close()

class Parser(object):
	def __init__(self, filename='', host='', port=8500, password='', ircHook=False, ircControlPort=5124):
		self.host = host
		self.port = port
		self.password = password
		self.ircHook = ircHook
		self.ircControlPort = ircControlPort
		if host != '':
			self.sock = socket.socket()
			self.sock.connect((host, port))
			self.sock.sendall(hashlib.sha256(password).hexdigest())
			rc = self.sock.recv(1024)
			if rc == 'OK':
				cmd = {'cmd': 'pull', 'args': ''}
				self.sock.sendall(json.dumps(cmd) + chr(4))

				rc = ''
				while rc[-1:] != chr(4):
					rc += self.sock.recv(4096)
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
			elif lines[0].lower() == '[pickle]':
				self.dbtype = 'pickle'
				self.dictionary = SafeUnpickler.loads(txt[len('[pickle]\n'):])
			else:
				raise Exception('Invalid database type')
		else:
			raise Exception('File does not exist')
		if ircHook:
			self.tempdict = copy.deepcopy(self.dictionary)
	def hash(self):
		for entry in self.dictionary['items']:
			if entry.get('hash') == None:
				entry['hash'] = hashlib.sha256(entry['name'] + str(time.time())).hexdigest()
	def save(self):
		self.hash()
		if self.host == '':
			f = open(self.filename, 'w')
			f.write('[' + self.dbtype + ']\n')

			if self.dbtype == 'pickle':
				f.write(pickle.dumps(self.dictionary))
			elif self.dbtype == 'json':
				f.write(json.dumps(self.dictionary))
			f.close()
		else:
			self.sock.sendall(json.dumps({'cmd': 'push', 'args': json.dumps(self.dictionary)}) + chr(4)) #jsonception
			sleep(0.2)
			self.sock.sendall(json.dumps({'cmd': 'save'}) + chr(4))

		if self.ircHook:
			ts = socket.socket()
			ts.connect(('localhost', self.ircControlPort))

			messages = {'lastwatched': {'norm': 'Watched %difference% episode%diffplural% [%old% to %new%]', 'noint': 'Watched from episode %old% to %new%'}, 'status': {'norm': chr(3) + '%ocolor%%oldstatus%'+ chr(15) +' -> '+ chr(3) +'%ncolor%%newstatus%'}, 'obs': {'norm': 'Observations: "%old%" --> "%new%"'}}
			ccolors = {'w': '3', 'd': '4', 'q': '6', 'c': '2', 'h': '7'}

			hashesMatched = []
			for new_entry in self.dictionary['items']:
				for old_entry in self.tempdict['items']:
					if new_entry['hash'] == old_entry['hash']:
						hashesMatched.append(new_entry['hash'])
						for key in messages:
							if new_entry[key] != old_entry[key]:
								if str(new_entry[key]).isdigit() and str(old_entry[key]).isdigit():
									smsg = messages[key]['norm'].replace('%difference%', str(int(new_entry[key]) - int(old_entry[key])))
									smsg = smsg.replace('%diffplural%', '' if (int(new_entry[key]) - int(old_entry[key])) == 1 else 's')
								else:
									try:
										smsg  = messages[key]['noint']
									except KeyError:
										smsg = messages[key]['norm']
								smsg = smsg.replace('%ocolor%', ccolors[old_entry['status'].lower()])
								smsg = smsg.replace('%ncolor%', ccolors[new_entry['status'].lower()])
								smsg = smsg.replace('%old%', str(old_entry[key]))
								smsg = smsg.replace('%new%', str(new_entry[key]))
								smsg = smsg.replace('%oldstatus%', utils.translated_status[old_entry['type']][old_entry['status'].lower()])
								smsg = smsg.replace('%newstatus%', utils.translated_status[new_entry['type']][new_entry['status'].lower()])
								ts.sendall(json.dumps({'action': 'msg', 'value': chr(2) + '[' + self.dictionary['name'] + chr(15) + chr(2) + ' -' + chr(3) + '2 ' + new_entry['name'] + chr(15) + '] ' + smsg}))
								break

			for entry in self.dictionary['items']:
				if (entry['hash'] in hashesMatched) == False:
					smsg = 'Added ' + chr(2) + chr(3) + '02%name%' + chr(15) + ' (' + chr(3) + '%ocolor%%status%' + chr(15) + ')'
					smsg = smsg.replace('%ocolor%', ccolors[entry['status'].lower()])
					smsg = smsg.replace('%name%', entry['name'])
					smsg = smsg.replace('%status%', utils.translated_status[entry['type']][entry['status'].lower()])
					ts.sendall(json.dumps({'action': 'msg', 'value': chr(2) + '[' + self.dictionary['name'] + '] ' + chr(15) + smsg}))

			for entry in self.tempdict['items']:
				if (entry['hash'] in hashesMatched) == False:
					smsg = 'Removed ' + chr(2) + chr(3) + '02%name%' + chr(15)
					smsg = smsg.replace('%name%', entry['name'])
					ts.sendall(json.dumps({'action': 'msg', 'value': chr(2) + '[' + self.dictionary['name'] + '] ' + chr(15) + smsg}))

			#ts.sendall(json.dumps({'action': 'msg', 'value': 'Something was changed on a database, don\'t ask what'}))
			ts.close()
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


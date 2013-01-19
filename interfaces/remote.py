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
import hashlib
from interfaces.common import *
import socket
import SocketServer
import json
from StringIO import StringIO

port = 8500
password = ''
dbs = []
curdb = 0

class rServer(SocketServer.BaseRequestHandler):
	def setup(self):
		global password
		print '[INFO] ' + repr(self.client_address) + ' connected'

		try:
			hashed_pass = self.request.recv(4096).strip('\n').strip('\r')
		except:
			print '[INFO] '+ repr(self.client_addess) + ' has disconnected'
			return

		if hashed_pass != password:
			self.request.send('305 NOT AUTHORIZED')
			print '[INFO] ' + repr(self.client_address) + ' has sent an invalid password and is now disconnected'
			self.request.close()
		else:
			print '[INFO] ' + repr(self.client_address) + ' has successfully logged in'
			self.request.send('OK')
			try:
				self.conns[self.request] = ''
			except:
				self.conns = {}
				self.conns[self.request] = ''

	def handle(self):
		#self.client_address[0] == ip (str)
		#self.request == socket.socket
		global dbs
		global curdb

		data = 'that4chanwolf is gentoo'
		wholething = ''
		while data:
			try:
				data = self.request.recv(4096)
			except:
				continue
			if (self.request in self.conns) == False: continue
			self.conns[self.request] += data.replace('\n', '').replace('\r', '')
			if self.conns[self.request][-1:] == chr(4):
				cmd = json.load(StringIO(self.conns[self.request][:-1]))
				print '[DEBUG] {CMD received} cmd=' + repr(cmd['cmd']) + ' args=' + repr(cmd['args'])
				self.conns[self.request] = ''

				if cmd['cmd'] == 'pull':
					res = {'cmd': cmd['cmd'], 'response': ''}
					res['response'] = json.dumps(dbs[curdb].dictionary)
					self.request.send(json.dumps(res) + chr(4))
				elif cmd['cmd'] == 'push':
					dbs[curdb].dictionary = json.loads(StringIO(cmd['args']))

					res = {'cmd': cmd['cmd'], 'response': 'OK'}
					self.request.send(json.dumps(res) + chr(4))
				continue

	def finish(self):
		print '[INFO] A client has disconnected'

colors = utils.colors()
def main(argv):
	global port
	global password
	global dbs
	files = []

	i = 0
	for arg in argv:
		if os.path.exists(arg):
			files.append(arg)
		elif arg in ['--pass', '--password']:
			if len(argv) <= i:
				print colors.fail + 'Missing password' + colors.default
				sys.exit(1)
			elif argv[i+1].startswith('--'):
				print colors.fail + 'Missing password' + colors.default
				sys.exit(1)	
			else:
				password = hashlib.sha256(argv[i+1]).hexdigest()
		elif arg in ['--port']:
			if len(argv) <= i:
				print colors.fail + 'Missing port' + colors.default
				sys.exit(1)
			elif argv[i+1].startswith('--') or argv[i+1].isdigit() == False:
				print colors.fail + 'Missing port' + colors.default
				sys.exit(1)	
			else:
				port = int(argv[i+1])
		i += 1
	if files == [] or password == '':
		print colors.bold + 'Usage: ' + colors.default + sys.argv[0] + ' [file, [file2, file3]] --password [pass] --port [number]'
		sys.exit(1)
	else:
		for fn in files:
			dbs.append(parser.Parser(fn))

		print '[INFO] Listening on port ' + str(port)
		rserver = SocketServer.ThreadingTCPServer(('', port), rServer)
		try:
			rserver.serve_forever()
		except KeyboardInterrupt:
			os.kill(os.getpid(), 9) #seppuku

def help():
	return 'Help page for remote interface'
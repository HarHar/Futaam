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
import socket
import socketserver
import json
from io import StringIO
from futaam.interfaces.common import *

port = 8500
password = ''
username = ''
dbs = []
curdb = 0
readonly = False
daemon = False

def nprint(s):
	global daemon
	if not daemon:
		print(s)

class rServer(socketserver.BaseRequestHandler):
	def setup(self):
		global password
		global username
		nprint('[INFO] ' + repr(self.client_address) + ' connected')

		try:
			login = self.request.recv(4096).strip('\n').strip('\r')
		except:
			nprint('[INFO] '+ repr(self.client_addess) + ' has disconnected')
			return

		if login != username + '/' + password:
			self.request.send('305 NOT AUTHORIZED')
			nprint('[INFO] ' + repr(self.client_address) + ' has sent an invalid password and is now disconnected')
			self.request.close()
		else:
			nprint('[INFO] ' + repr(self.client_address) + ' has successfully logged in')
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
		global readonly

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
				self.conns[self.request] = ''

				if cmd['cmd'] == 'pull':
					res = {'cmd': cmd['cmd'], 'response': ''}
					dbs[curdb].reload()
					res['response'] = json.dumps(dbs[curdb].dictionary)
					self.request.send(json.dumps(res) + chr(4))

					nprint('[INFO] ' + repr(self.client_address) + ' has pulled the database')
				elif cmd['cmd'] == 'push':
					if readonly:
						self.request.send(json.dumps({'cmd': cmd['cmd'], 'response': 'Read-only database'}) + chr(4))
						continue
					dbs[curdb].dictionary = json.load(StringIO(cmd['args']))

					res = {'cmd': cmd['cmd'], 'response': 'OK'}
					self.request.send(json.dumps(res) + chr(4))

					nprint('[INFO] ' + repr(self.client_address) + ' has pushed to the database')
				elif cmd['cmd'] == 'save':
					if readonly:
						self.request.send(json.dumps({'cmd': cmd['cmd'], 'response': 'Read-only database'}) + chr(4))
						continue
					dbs[curdb].save()

					res = {'cmd': cmd['cmd'], 'response': 'OK'}
					self.request.send(json.dumps(res) + chr(4))

					nprint('[INFO] ' + repr(self.client_address) + ' has saved the database')
				elif cmd['cmd'] == 'sdb':
					try:
						curdb += 1
						repr(dbs[curdb])
					except IndexError:
						curdb = 0

					res = {'cmd': cmd['cmd'], 'response': 'OK'}
					self.request.send(json.dumps(res) + chr(4))

					nprint('[INFO] ' + repr(self.client_address) + ' has switched to the next database')
				continue

	def finish(self):
		nprint('[INFO] A client has disconnected')

colors = utils.colors()
def main(argv, version):
	global daemon
	for opt in ['-d', '--daemon', '-f', '--fork']:
		if argv.__contains__(opt):
			daemon = True
			break

	if daemon:
		if os.fork() != 0:
			exit()

	global port
	global password
	global dbs
	global readonly
	global username
	files = []
	hooks = []

	# gather arguments
	files = ARGS.database
	password = ARGS.password
	port = ARGS.port
	readonly=ARGS.readonly
	if ARGS.hooks:
		hooks = ARGS.hooks

	if files == [] or password == '':
		nprint(colors.header + '[Usage] ' + colors.default + sys.argv[0] + ' [file, [file2, file3]] --username [user] --password [pass] --port [number]')
		sys.exit(1)
	else:
		for fn in files:
			dbs.append(parser.Parser(fn, hooks=hooks))

		nprint('[INFO] Listening on port ' + str(port))
		rserver = socketserver.ThreadingTCPServer(('', port), rServer)
		try:
			rserver.serve_forever()
		except KeyboardInterrupt:
			os.kill(os.getpid(), 9) #seppuku

def print_help():
	hlp = ''
	hlp += colors.header + '[Usage] ' + colors.default
	hlp += sys.argv[0] + ' [file, [file2, file3]] --password [pass] --port [number] [--readonly]\n'
	return hlp

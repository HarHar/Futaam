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
from twisted.internet import reactor, protocol
from twisted.words.protocols import irc
import socket
import os
import SocketServer
import threading
import json
controlPort = 5124

class controlSocket(SocketServer.BaseRequestHandler):
	def setup(self):
		pass
	def handle(self):
		data = 'dummy text'
		global bot
		while data:
			try:
				data = self.request.recv(4096).replace('\r', '').replace('\n', '')
			except:
				continue
			try:
				dec = json.loads(data)
			except:
				continue
			if dec.get('action') == 'msg':
				bot._msg(dec['value'])
			elif dec.get('action') == 'join':
				try:
					bot.join(str(dec['value']))
				except:
					pass
			elif dec.get('action') == 'part':
				try:
					bot.part(str(dec['value']))
				except:
					pass
	def finish(self):
		pass

def csStart():
	SocketServer.ThreadingTCPServer(('localhost', controlPort), controlSocket).serve_forever()
	print '[FATAL] IRC control port has closed'
	os.kill(os.getpid(), 9)

class IRCProtocol(irc.IRCClient):
	nickname = "FutaBot-"
	def connectionMade(self):
		global bot
		global nick
		self.nickname = nick
		bot = self
		irc.IRCClient.connectionMade(self)

	def signedOn(self):
		print 'Success! Connection established.'
		self.join(self.factory.channel)
		print 'Joined channel', self.factory.channel

	def privmsg(self, user, channel, msg):
		user = user.split('!', 1)[0]
		print 'USER=' + repr(user) + ' channel='+repr(channel) + ' msg='+repr(msg)

	def _msg(self, msg):
		self.msg(self.factory.channel, str(msg.encode('utf8')))

class IRCFactory(protocol.ClientFactory):
    protocol = IRCProtocol

    def __init__(self, channel, nicky):
    	global nick
    	nick = nicky
        self.channel = channel

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed because of %s" % reason
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "Connection lost: %s" % reason
        connector.connect()

def main(argv):
	host = ''
	channel = ''
	nickname = 'FutaBot'
	port = 6667
	i = 0
	for arg in argv:
		if arg == '--host':
			if len(argv) <= i:
				print 'Missing host'
				exit()
			elif argv[i+1].startswith('--'):
				print 'Missing host'
				exit()
			else:
				host = argv[i+1]
		elif arg == '--chan' or arg == '--channel':
			if len(argv) <= i:
				print 'Missing channel'
				exit()
			elif argv[i+1].startswith('--'):
				print 'Missing channel'
				exit()
			else:
				channel = argv[i+1]
		elif arg == '--port':
			if len(argv) <= i:
				print 'Missing port'
				exit()
			elif argv[i+1].isdigit() == False:
				print 'Invalid port'
				exit()
			else:
				port = int(argv[i+1])
		elif arg == '--nick' or arg == '--nickname':
			if len(argv) <= i:
				print 'Missing nick'
				exit()
			elif argv[i+1].startswith('--'):
				print 'Missing nick'
				exit()
			else:
				nickname = argv[i+1]			
		i += 1
	try:
		socket.socket().connect(('localhost', controlPort))
	except socket.error:
		if host == '' or channel == '':
			print 'IRC server and/or channel not specified'
			print 'Use: --host [irc server] --channel [name]'
			exit()
		print 'IRC control port refused connection, starting IRC daemon...'

		if os.fork() != 0:
			exit()

		try:
			t = threading.Thread(target=csStart)
			t.setDaemon(True)
			t.start()
		except:
			exit()

		global fact
		fact = IRCFactory(channel, nickname)
		reactor.connectTCP(host, port, fact)
		reactor.run()
		os.kill(os.getpid(), 9) #otherwise the thread will make it hang :\

def help():
	return 'Help page for irc interface'
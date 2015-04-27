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
import socketserver
import threading
import json
import platform
from futaam.interfaces.common import colors
controlPort = 5124
colors = utils.colors()


class controlSocket(socketserver.BaseRequestHandler):

    def setup(self):
        pass

    def handle(self):
        data = 'dummy text'
        global bot
        while data:
            try:
                data = self.request.recv(4096).replace(
                    '\r', '').replace('\n', '')
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
    socketserver.ThreadingTCPServer(
        ('localhost', controlPort), controlSocket).serve_forever()
    print('[FATAL] IRC control port has closed')
    os.kill(os.getpid(), 9)


class IRCProtocol(irc.IRCClient):
    nickname = "FutaBot-"

    def __init__(self, version):
        self.versionNum = version

    def connectionMade(self):
        global bot
        global nick
        self.nickname = nick
        self.versionName = 'Futaam announce Bot'
        self.versionEnv = platform.platform()
        bot = self
        irc.IRCClient.connectionMade(self)

    def signedOn(self):
        self.join(self.factory.channel)

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]

    def _msg(self, msg):
        self.msg(self.factory.channel, str(msg.encode('utf8')))


class IRCFactory(protocol.ClientFactory):

    def __init__(self, channel, nicky, version):
        global nick
        nick = nicky
        protocol = IRCProtocol(version)
        self.channel = channel

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed because of %s" % reason)
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost: %s" % reason)
        connector.connect()


def main(argv, version):
    host = ''
    channel = ''
    nickname = 'FutaBot'
    port = 6667
	# gather arguments
    if ARGS.host:
        host = ARGS.host
    password = ''
    if ARGS.channel:
        channel = ARGS.channel
    if ARGS.port:
        port = ARGS.port
    hooks = []
    if ARGS.nick:
        nickname = ARGS.nick
	
    try:
        socket.socket().connect(('localhost', controlPort))
    except socket.error:
        if host == '' or channel == '':
            print('IRC server and/or channel not specified')
            print('Use: --host [irc server] --channel [name]')
            exit()
        print('IRC control port refused connection, starting IRC daemon...')

        if os.fork() != 0:
            exit()

        try:
            t = threading.Thread(target=csStart)
            t.setDaemon(True)
            t.start()
        except:
            exit()

        global fact
        fact = IRCFactory(channel, nickname, version)
        reactor.connectTCP(host, port, fact)
        reactor.run()
        os.kill(os.getpid(), 9)  # otherwise the thread will make it hang :\
    print('IRC bot daemon already running')
    print('Choose another interface and use the argument --ircnotify')


def print_help():
    ret = colors.bold + 'Interface parameters:' + colors.default + \
        ' --host [irc server] --port [number] --channel [#chan] --nick [nick]'
    ret += '\n\tThis will spawn a bot daemon, it will connect and join the specified channel,'
    ret += '\n\tAfter that, use your favorite interface with the argument --ircnotify'
    return ret

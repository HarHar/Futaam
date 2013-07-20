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

import curses
import sys
import os
import threading
from interfaces.common import *
import locale
import urllib2
from time import sleep as sleep
import getpass

locale.setlocale(locale.LC_ALL,"")
colors = utils.colors()
MAL = utils.MALWrapper()
vndb = utils.VNDB('Futaam', '0.1')

class if_ncurses(object):
	##These functions must come first
	def get_terminal_size(self, fd=1):
	    """
	    Returns height and width of current terminal. First tries to get
	    size via termios.TIOCGWINSZ, then from environment. Defaults to 25
	    lines x 80 columns if both methods fail.
	    :param fd: file descriptor (default: 1=stdout)
	    """
	    try:
	        import fcntl, termios, struct
	        hw = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
	    except:
	        try:
	            hw = (os.environ['LINES'], os.environ['COLUMNS'])
	        except:  
	            hw = (25, 80)
	 
	    return hw

	def get_terminal_height(self, fd=1):
	    """
	    Returns height of terminal if it is a tty, 999 otherwise
	    :param fd: file descriptor (default: 1=stdout)
	    """
	    if os.isatty(fd):
	        height = self.get_terminal_size(fd)[0]
	    else:
	        height = 999
	 
	    return height
 
	def get_terminal_width(self, fd=1):
	    """
	    Returns width of terminal if it is a tty, 999 otherwise
	 
	    :param fd: file descriptor (default: 1=stdout)
	    """
	    if os.isatty(fd):
	        width = self.get_terminal_size(fd)[1]
	    else:
	        width = 999
	 
	    return width

	def __init__(self, argv):
		self.curitem = 0
		self.dbfile = []
		self.host = ''
		self.port = 8500
		i = 0
		self.password = ''
		self.username = ''
		self.hooks = []
		for x in argv:
			if os.path.exists(x):
				self.dbfile.append(x)
			elif x == '--host':
				if len(argv) <= i:
					print colors.fail + 'Missing host' + colors.default
					sys.exit(1)
				elif argv[i+1].startswith('--'):
					print colors.fail + 'Missing host' + colors.default
					sys.exit(1)	
				else:
					self.host = argv[i+1]
			elif x == '--port':
				if len(argv) <= i:
					print colors.fail + 'Missing port' + colors.default
					sys.exit(1)
				elif argv[i+1].startswith('--') or argv[i+1].isdigit() == False:
					print colors.fail + 'Missing port' + colors.default
					sys.exit(1)	
				else:
					self.port = int(argv[i+1])
			elif x == '--username':
				if len(argv) <= i:
					print colors.fail + 'Missing username' + colors.default
					sys.exit(1)
				elif argv[i+1].startswith('--'):
					print colors.fail + 'Missing username' + colors.default
					sys.exit(1)	
				else:
					self.username = argv[i+1]
			elif x == '--hook':
				if len(argv) <= i:
					print colors.fail + 'Missing hook name' + colors.default
					sys.exit(1)
				elif argv[i+1].startswith('--'):
					print colors.fail + 'Missing hook name' + colors.default
					sys.exit(1)
				else:
					if not (argv[i+1] in parser.availableHooks):
						print colors.fail + 'Hook not available' + colors.default
						sys.exit(1)
					else:
						self.hooks.append(parser.availableHooks[argv[i+1]]())
			elif x == '--list-hooks':
				for hook in parser.availableHooks:
					print colors.header + hook + colors.default + ': ' + parser.availableHooks[hook].__doc__
				sys.exit(0)
			i += 1	

		if len(self.dbfile) == 0 and self.host == '':
			print colors.fail + 'No database file specified' + colors.default
			sys.exit(1)

		if self.host == '':
			self.dbs = []
			for fn in self.dbfile:
				self.dbs.append(parser.Parser(fn, hooks=self.hooks))
			self.currentdb = 0
		else:
			if self.username == '':
				print colors.fail + 'Missing username! ' + colors.default + 'Use "--username [user]"'
				sys.exit(1)
			self.username = getpass.getpass('Password for ' + username + '@' + host + ': ')
			self.dbs = []
			self.dbs.append(parser.Parser(host=self.host, port=self.port, username=self.username, password=self.password, hooks=self.hooks))
			self.currentdb = 0

		self.showing = []
		self.range_min = 0
		self.range_max = self.get_terminal_height()
		self.screen = curses.initscr()
		self.screen.keypad(1)
		curses.cbreak()
		curses.noecho()
		curses.curs_set(0)
		curses.start_color()
		curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK) 
		curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK) 
		curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK) 
		curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
		curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

		#self.footer = '[Q]uit / [D]elete / [E]dit / [A]dd / [S]ynopsis / [I]mage'
		self.footer = '[Q]uit / [H]elp'
		self.f2 = self.footer

		self.redraw()
		self.drawitems()
		while True:
			try:
				x = self.screen.getch()
			except:
				curses.nocbreak()
				stdscr.keypad(0)
				curses.echo()
				curses.curs_set(1)
				curses.endwin()
			
			if x == curses.KEY_RESIZE: self.showing = []; self.range_min = 0; self.range_max = 0; self.redraw(); self.drawitems(); continue

			if x == ord('q') or x == ord('Q') or x == 27:
				curses.endwin()
				sys.exit(0)
			if x == ord('h') or x == ord('H'):
				if self.get_terminal_height() < 13:
					self.alert('Screen too small')
				else:
					self.redraw(True)
					self.screen.addstr(2, 1, '[Q]uit', curses.color_pair(4))
					self.screen.addstr(3, 1, '[D]elete', curses.color_pair(4))
					self.screen.addstr(4, 1, '[E]dit', curses.color_pair(4))
					self.screen.addstr(5, 1, '[A]dd', curses.color_pair(4))
					self.screen.addstr(6, 1, '[S]ynopsis', curses.color_pair(4))
					self.screen.addstr(7, 1, '[I]mage', curses.color_pair(4))
					#purposefully skip one
					self.screen.addstr(9, 1, '[F5] Move highlighted entry up', curses.color_pair(4))
					self.screen.addstr(10, 1, '[F6] Move highlighted entry down', curses.color_pair(4))

					self.screen.addstr(self.get_terminal_height() - 2, 1, 'Press any key to go back', curses.color_pair(4))
					self.screen.getch()

				self.redraw()
				self.drawitems()
			elif x == ord('S') or x == ord('s'):
				self.drawinfo()
				continue
			elif x == ord('a') or x == ord('A'):
				self.addEntry()
			elif x == ord('d') or x == ord('D'):
				for entry in self.dbs[self.currentdb].dictionary['items']:
					if entry['id'] == self.curitem:
						self.dbs[self.currentdb].dictionary['items'].remove(entry)
						self.dbs[self.currentdb].dictionary['count'] -= 1
						break
				else:
					continue

				##### REBUILD IDS #####
				for x in xrange(0, self.dbs[self.currentdb].dictionary['count']):
					self.dbs[self.currentdb].dictionary['items'][x]['id'] = x
				#######################
				self.dbs[self.currentdb].save()
				self.redraw()
				self.drawitems()
			elif x == ord('e') or x == ord('E'):
				self.edit()
			elif x == ord('i') or x == ord('I'):
				self.sI()
			elif x == 258: #DOWN
				if len(self.dbs[self.currentdb].dictionary['items'])-1 == self.curitem:
					continue
				self.curitem += 1
				self.redraw()
				self.drawitems()
			elif x == 259: #UP
				if self.curitem == 0:
					continue
				self.curitem -= 1
				self.redraw()
				self.drawitems(direction=1)
			elif x == 338:
				size = self.get_terminal_size()
				itemsCount = len(self.dbs[self.currentdb].dictionary['items'])-1

				page = size[0] - 4

				target = self.curitem + page - 1

				if target >= itemsCount:
					target = itemsCount

				self.curitem = target
				self.redraw()
				self.drawitems()
			elif x == 339:
				size = self.get_terminal_size()
				itemsCount = len(self.dbs[self.currentdb].dictionary['items'])-1

				page = size[0] - 4

				target = self.curitem - page + 1

				if target <= 0:
					target = 0

				self.curitem = target
				self.redraw()
				self.drawitems()
			elif x == curses.KEY_F5:
				#Move up
				if self.curitem == 0:
					continue

				self.dbs[self.currentdb].dictionary['items'][self.curitem]['id'] = self.curitem - 1
				self.dbs[self.currentdb].dictionary['items'][self.curitem - 1]['id'] = self.curitem
				self.dbs[self.currentdb].dictionary['items'] = sorted(self.dbs[self.currentdb].dictionary['items'], key=lambda x: x['id'])
				self.dbs[self.currentdb].save()

				self.showing[self.curitem - self.range_min]['id'] = self.curitem - 1
				self.showing[(self.curitem - self.range_min) - 1]['id'] = self.curitem
				self.showing = sorted(self.showing, key=lambda x: x['id'])

				self.curitem = self.curitem - 1
				self.redraw()
				self.drawitems()
			elif x == curses.KEY_F6:
				#Move down
				if self.curitem >= len(self.dbs[self.currentdb].dictionary['items']) -1:
					continue

				self.dbs[self.currentdb].dictionary['items'][self.curitem]['id'] = self.curitem + 1
				self.dbs[self.currentdb].dictionary['items'][self.curitem + 1]['id'] = self.curitem
				self.dbs[self.currentdb].dictionary['items'] = sorted(self.dbs[self.currentdb].dictionary['items'], key=lambda x: x['id'])
				self.dbs[self.currentdb].save()

				self.showing[self.curitem - self.range_min]['id'] = self.curitem + 1
				self.showing[(self.curitem - self.range_min) + 1]['id'] = self.curitem
				self.showing = sorted(self.showing, key=lambda x: x['id'])

				self.curitem = self.curitem + 1
				self.redraw()
				self.drawitems()
			else:
				pass
				#self.screen.addstr(10, 10, str(x))		

	def addEntry(self):
		self.redraw(True)
		self.screen.addstr(2, 2, 'Press A for anime')
		self.screen.addstr(3, 2, 'Press M for manga')
		self.screen.addstr(4, 2, 'Press C to cancel')
		x = 0
		while (x in [ord('a'), ord('m'), ord('A'), ord('M'), ord('c'), ord('C')]) == False:
			x = self.screen.getch()
		if x in [ord('c'), ord('C')]:
			self.redraw()
			self.drawitems()
			return
		elif x in [ord('a'), ord('A')]:
			t = 'anime'
		else:
			t = 'manga'

		self.redraw(True)
		name = self.prompt('Name: ', 2)
		searchResults = MAL.search(name, t)
		if len(searchResults) == 0:
			self.alert(t[0].upper() + t[1:].lower() + ' not found on MAL :\\') #this will be better handled on the future
			self.redraw()
			self.drawitems()
			return
		i = 0
		for x in searchResults:
			searchResults[i]['index'] = i
			searchResults[i]['am'] = t
			i += 1
		self.footer = '[ENTER] Choose / [C] Cancel'
		self.redraw()
		self.scuritem = 0
		self.drawSearch(searchResults)
		while True:
			x = self.screen.getch()
			if x == 258: #DOWN
				if len(searchResults)-1 == self.scuritem:
					continue
				self.scuritem += 1
				self.redraw()
				self.drawSearch(searchResults)
			elif x == 259: #UP
				if self.scuritem == 0:
					continue
				self.scuritem -= 1
				self.redraw()
				self.drawSearch(searchResults)
			elif x == ord('c') or x == ord('C'):
				self.footer = f2
				self.redraw()
				self.drawitems()
				return
			elif x == 10:
				malanime = searchResults[self.scuritem]
				deep = MAL.details(malanime['id'], t)
				g = ''
				for genre in deep['genres']:
					g = g + genre + '/'
				genre = g[:-1]
				title = deep['title']
				self.redraw(True)
				self.screen.addstr(2, 2, '[Status]', curses.A_BOLD)
				self.screen.addstr(3, 2, '[W] - ' + utils.translated_status[t]['w'])
				self.screen.addstr(4, 2, '[C] - ' + utils.translated_status[t]['c'])
				self.screen.addstr(5, 2, '[Q] - ' + utils.translated_status[t]['q'])
				self.screen.addstr(6, 2, '[H] - ' + utils.translated_status[t]['h'])
				self.screen.addstr(7, 2, '[D] - ' + utils.translated_status[t]['d'])
				x = ''
				while (x.lower() in ['w', 'c', 'q', 'h', 'd']) == False:
					x = self.screen.getch()
					if x > 256:
						continue
					x = chr(x)
				if x.lower() == 'w':
					if t == 'anime':
						lastEp = str(malanime['episodes'])
					else:
						lastEp = str(malanime['chapters'])
				elif x.lower() == 'q':
					lastEp = ''
					pass
				else:
					if t == 'anime':
						lastEp = self.prompt('<Last episode watched> ', 8).replace('\n', '')
					else:
						lastEp = self.prompt('<Last chapter read> ', 9).replace('\n', '')
				obs = self.prompt('<Observations> ', 10).replace('\n', '')

				try:
					self.dbs[self.currentdb].dictionary['count'] += 1
				except:
					self.dbs[self.currentdb].dictionary['count'] = 1
				self.dbs[self.currentdb].dictionary['items'].append({'id': self.dbs[self.currentdb].dictionary['count'], 'type': t, 'aid': malanime['id'], 'name': utils.HTMLEntitiesToUnicode(utils.remove_html_tags(title)), 'genre': utils.HTMLEntitiesToUnicode(utils.remove_html_tags(genre)), 'status': x.lower(), 'lastwatched': lastEp, 'obs': obs})
				for x in xrange(0, self.dbs[self.currentdb].dictionary['count']):
					self.dbs[self.currentdb].dictionary['items'][x]['id'] = x	
				self.dbs[self.currentdb].save()
				self.screen.addstr(11, 2, 'Entry added!', curses.color_pair(3) + curses.A_REVERSE)
				self.screen.refresh()
				sleep(2)
				self.footer = self.f2
				self.redraw()
				self.drawitems()
				return
	def alert(self, s, time=2):
		terminalsize = self.get_terminal_size()
		self.redraw(True)
		x_m = terminalsize[0] / 2
		x_y = (terminalsize[1] / 2) - (len(s) / 2)

		self.screen.addstr(x_m-1, x_y-1, ' ' * (len(s) + 2), curses.color_pair(1) + curses.A_REVERSE)
		self.screen.addstr(x_m, x_y-1, ' ', curses.color_pair(1) + curses.A_REVERSE)
		self.screen.addstr(x_m, x_y, s, curses.color_pair(1))
		self.screen.addstr(x_m, x_y+len(s), ' ', curses.color_pair(1) + curses.A_REVERSE)
		self.screen.addstr(x_m+1, x_y-1, ' ' * (len(s) + 2), curses.color_pair(1) + curses.A_REVERSE)

		self.screen.refresh()
		sleep(time)
	def edit(self):
		terminalsize = self.get_terminal_size()
		entry = self.dbs[self.currentdb].dictionary['items'][self.curitem]
		self.redraw()
		self.drawitems(True)

		changefields = [{'dbentry': 'name', 'prompt': 'Title: '}, {'dbentry': 'genre', 'prompt': 'Genre: '}, {'dbentry': 'status', 'prompt': 'Status: '}, {'dbentry': 'lastwatched', 'prompt': 'Last watched: '}, {'dbentry': 'obs', 'prompt': 'Observations: '}]

		#Screen size check
		for field in changefields:
			if (len(self.dbs[self.currentdb].dictionary['items'][self.curitem][field['dbentry']]) + len(field['prompt']) + 27) > terminalsize[1]:
				self.alert('Screen too small')
				self.redraw()
				self.drawitems()
				return

		t = 1
		for field in changefields:
			if field['dbentry'] == 'status':
				self.screen.addstr(t, 27, 'Status [W/C/Q/H/D]')
				x = ''
				while (x.lower() in ['w', 'c', 'q', 'h', 'd']) == False:
					x = self.screen.getch()
					if x > 256:
						continue
					x = chr(x)
				self.dbs[self.currentdb].dictionary['items'][self.curitem]['status'] = x.lower()
				t += 1
				continue
			self.dbs[self.currentdb].dictionary['items'][self.curitem][field['dbentry']] = self.prompt(field['prompt'], t, 27, entry[field['dbentry']])
			t += 1
		self.screen.addstr(t+1, 27, 'Entry edited!', curses.color_pair(3) + curses.A_REVERSE)
		self.screen.refresh()
		sleep(2)
		self.dbs[self.currentdb].save()
		self.redraw()
		self.drawitems()

	def prompt(self, p, line, y=2, default=''):
		terminalsize = self.get_terminal_size()
		curses.curs_set(1)
		self.screen.addstr(line, y, p, curses.A_BOLD)
		self.screen.refresh()
		self.screen.addstr(line, len(p) + y, ' '*15, curses.A_REVERSE)
		ret = default
		x = 0
		w = len(p) + y
		if default != '':
			self.screen.addstr(line, w, default, curses.A_REVERSE)
			w += len(default)

		while x != 10:
			x = self.screen.getch()
			if x == 263: #backspace
				if w <= len(p) + y:
					continue
				self.screen.addstr(line, w-1, ' ', curses.A_REVERSE)
				self.screen.addstr(line, w-1, '', curses.A_REVERSE)
				w -= 1
				ret = ret[:-1]
				continue
			if w > terminalsize[1]-5:
				continue
			try:
				self.screen.addstr(line, w, unichr(x), curses.A_REVERSE)
			except:
				continue
			w += 1
			ret += unichr(x)
		ret = ret.replace('\n', '')
		curses.curs_set(0)
		return ret

	def drawSearch(self, searchResults):
		terminalsize = self.get_terminal_size()
		if terminalsize[0] < 12 or terminalsize[1] < 46:
			self.screen.keypad(0)
			curses.endwin()
			print colors.fail + '\nScreen too small :C' + colors.default
			sys.exit(1)
		i = 0
		y = 1
		x = 2
		if self.scuritem > (terminalsize[0]-5):
			showing = searchResults[scuritem-terminalsize[0]+5:self.scuritem+1]
		else:
			showing = searchResults[:terminalsize[0]-4]
		for entry in showing:
			if len(entry['title']) >= 23:
				name = entry['title'][:20] + '...'
			else:
				name = entry['title']
			if entry['index'] == self.scuritem:
				bold = curses.A_REVERSE
				if entry['am'] == 'anime':
					fields = {'Title: ': entry['title'], 'Type: ': entry['type'], 'Episodes: ': str(entry['episodes']), 'Status: ': entry['status']}
				else:
					fields = {'Title: ': entry['title'], 'Type: ': entry['type'], 'Chapters: ': str(entry['chapters']), 'Status: ': entry['status']}
				t = 1
				for field in fields:
					if fields[field] == None: fields[field] = ''
					self.screen.addstr(t, 27, field, curses.A_BOLD)
					sizeleft = int(terminalsize[1]) - int(len(field) + len(fields[field])) - 28
					if sizeleft <= 3:
						self.screen.addstr(t, 27 + len(field), fields[field][:sizeleft-3].encode('utf-8') + '...')
						t += 1
						continue
					fix = ' ' * sizeleft
					self.screen.addstr(t, 27 + len(field), fields[field].encode('utf-8') + fix)
					t += 1
				s = 27
				l = t + 1
				workwidth = terminalsize[1] - s-1
				self.screen.addstr(l, s, 'Synopsis: ', curses.A_BOLD)
				if len(entry['synopsis']) < workwidth:
					self.screen.addstr(l, s + len('Synopsis: '), entry['synopsis'])
				else:
					self.screen.addstr(l, s + len('Synopsis: '), utils.HTMLEntitiesToUnicode(entry['synopsis'][:workwidth-len('Synopsis: ')]).encode('utf-8'))
					t = workwidth-len('Synopsis: ')
					while len(entry['synopsis'][t:t+workwidth]) != 0:
						l += 1
						if l >= terminalsize[0]-5:
							self.screen.addstr(l, s, utils.HTMLEntitiesToUnicode(utils.remove_html_tags(entry['synopsis'][t:t+workwidth-3].replace('\n', '').replace('\r', '') + '...')).encode('utf-8'))
							break
						self.screen.addstr(l, s, utils.HTMLEntitiesToUnicode(utils.remove_html_tags(entry['synopsis'][t:t+workwidth].replace('\n', '').replace('\r', ''))).encode('utf-8'))
						t += workwidth				
			else:
				bold = 0

			name = name.encode('utf-8')
			self.screen.addstr(x, y, name, bold)

			x += 1
			i += 1		

	def redraw(self, noxtra=False):
		terminalsize = self.get_terminal_size()
		self.screen.clear()
		self.screen.border(0)
		self.screen.addstr(0, 2, self.dbs[self.currentdb].dictionary['name'] + ' - ' + self.dbs[self.currentdb].dictionary['description'], curses.color_pair(1))
		if noxtra == False:
			for line in range(1, terminalsize[0]-1):
				self.screen.addstr(line, 25, u'│'.encode('utf-8'))

			self.screen.addstr(terminalsize[0]-2, 1, self.footer)

	def drawitems(self, noSidePanel=False, direction=0):
		terminalsize = self.get_terminal_size()
		if terminalsize[0] < 12 or terminalsize[1] < 46:
			self.screen.keypad(0)
			curses.endwin()
			print colors.fail + '\nScreen too small :C' + colors.default
			sys.exit(1)
		i = 0
		y = 1
		x = 2
		#if self.curitem > (terminalsize[0]-5):
		#	showing = self.dbs[self.currentdb].dictionary['items'][self.curitem-terminalsize[0]+5:self.curitem+1]
		#else:
		#	showing = self.dbs[self.currentdb].dictionary['items'][:terminalsize[0]-4]

		##self.showing
		for entry in self.showing:
			if entry['id'] == self.curitem:
				#it's on the list, don't do anything
				break
		else:
			if self.curitem > (terminalsize[0]-5):
				if direction == 0:
					self.showing = self.dbs[self.currentdb].dictionary['items'][self.curitem-terminalsize[0]+5:self.curitem+1]
					self.range_min = self.curitem-terminalsize[0]+5
					self.range_max = self.curitem+1
				elif direction == 1: #UP
					self.showing = self.dbs[self.currentdb].dictionary['items'][self.curitem:terminalsize[0]+self.curitem-5]
					self.range_min = self.curitem
					self.range_max = terminalsize[0]+self.curitem-5
			else:
				self.showing = self.dbs[self.currentdb].dictionary['items'][:terminalsize[0]-4]
				self.range_min = 0
				self.range_max = terminalsize[0]-4


		for entry in self.showing:
			if len(entry['name']) >= 23:
				name = entry['name'][:20] + '...'
			else:
				name = entry['name']
			if entry['id'] == self.curitem:
				bold = curses.A_REVERSE
				if noSidePanel == False:
					if entry['type'] == 'anime':
						fields = (('Title: ', entry['name']), ('Genre: ', entry['genre']), ('Status: ', translated_status[entry['type'].lower()][entry['status'].lower()]), ('Last watched: ', entry['lastwatched']), ('Observations: ', entry['obs']))
					elif entry['type'] == 'manga':
						fields = (('Title: ', entry['name']), ('Genre: ', entry['genre']), ('Status: ', translated_status[entry['type'].lower()][entry['status'].lower()]), ('Last chapter/volume read: ', entry['lastwatched']), ('Observations: ', entry['obs']))
					elif entry['type'] == 'vn':
						fields = (('Title: ', entry['name']), ('Status: ', translated_status[entry['type'].lower()][entry['status'].lower()]), ('Observations: ', entry['obs']))
					t = 1
					out = {'anime': 'Anime', 'manga': 'Manga', 'vn': 'VN'}[entry['type']]
					self.screen.addstr(terminalsize[0]-1, terminalsize[1]-len(out)-1, out, {'anime': curses.color_pair(3), 'manga': curses.color_pair(2), 'vn': curses.color_pair(5)}[entry['type']] + curses.A_REVERSE)
					del out
					for field in fields:
						self.screen.addstr(t, 27, field[0], curses.A_BOLD)
						if isinstance(field[1], basestring):
							showstr = field[1]
							sizeleft = int(terminalsize[1]) - int(len(str(field[0])) + len(field[1])) - 28
						else:
							showstr = str(field[1])
							sizeleft = int(terminalsize[1]) - int(len(str(field[0])) + len(str(field[1]))) - 28
						if sizeleft <= 3:
							self.screen.addstr(t, 27 + len(field[0]), field[1][:sizeleft-3].encode('utf-8') + '...')
							t += 1
							continue
						fix = ' ' * sizeleft
						self.screen.addstr(t, 27 + len(field[0]), showstr.encode('utf-8') + fix)
						t += 1
			else:
				bold = 0

			name = name.encode('utf-8')
			if entry['status'].lower() == 'w':
				self.screen.addstr(x, y, name, curses.color_pair(3) + bold)
			elif entry['status'].lower() == 'd':
				self.screen.addstr(x, y, name, curses.color_pair(1) + bold)
			elif entry['status'].lower() == 'c':
				self.screen.addstr(x, y, name, curses.color_pair(2) + bold)
			elif entry['status'].lower() == 'h':
				self.screen.addstr(x, y, name, curses.color_pair(4) + bold)
			elif entry['status'].lower() == 'q':
				self.screen.addstr(x, y, name, curses.color_pair(5) + bold)

			x += 1
			i += 1

	def sI(self):		
		entry = self.dbs[self.currentdb].dictionary['items'][self.curitem]
		if entry.get('aid') != None:
			try:
				self.screen.addstr(self.get_terminal_height()-1, 1, 'Fetching URL... Please wait', curses.color_pair(5))
				self.screen.refresh()
				if entry['type'] in ['anime', 'manga']:
					info = MAL.details(entry['aid'], entry['type'])
				elif entry['type'] == 'vn':
					info = vndb.get('vn', 'basic,details', '(id='+ str(entry['aid']) + ')', '')['items'][0]
				else: return
				self.screen.border()
			except urllib2.HTTPError, info:
				self.alert('Error: ' + str(info), 2)
				self.redraw()
				self.drawitems()
				return
			self.screen.addstr(self.get_terminal_height()-1, 1, 'Fetching image... Please wait', curses.color_pair(5))
			self.screen.refresh()
			utils.showImage(info['image' + {'anime': '_url', 'manga': '_url', 'vn': ''}[entry['type']]])
			self.screen.border()
			self.screen.addstr(0, 2, self.dbs[self.currentdb].dictionary['name'] + ' - ' + self.dbs[self.currentdb].dictionary['description'], curses.color_pair(1))


	def drawinfo(self):
		terminalsize = self.get_terminal_size()
		entry = self.dbs[self.currentdb].dictionary['items'][self.curitem]
		s = 27
		l = 7 if entry['type'] in ['anime', 'manga'] else 5 if entry['type'] == 'vn' else 7

		workwidth = terminalsize[1] - s-1
		n = 0
		
		if entry.get('aid') != None:
			try:
				self.screen.addstr(self.get_terminal_height()-1, 1, 'Fetching synopsis... Please wait', curses.color_pair(5))
				self.screen.refresh()
				if entry['type'] in ['anime', 'manga']:
					info = MAL.details(entry['aid'], entry['type'])
				elif entry['type'] == 'vn':
					info = vndb.get('vn', 'basic,details', '(id='+ str(entry['aid']) + ')', '')['items'][0]
					info['synopsis'] = info['description']
				else:
					return
				info['synopsis'] = utils.remove_html_tags(info['synopsis'])
				info['synopsis'] = info['synopsis'].replace('\n', ' | ')
				self.screen.border()
				out = {'anime': 'Anime', 'manga': 'Manga', 'vn': 'VN'}[entry['type']]
				self.screen.addstr(terminalsize[0]-1, terminalsize[1]-len(out)-1, out, {'anime': curses.color_pair(3), 'manga': curses.color_pair(2), 'vn': curses.color_pair(5)}[entry['type']] + curses.A_REVERSE)
				del out
				self.screen.addstr(0, 2, self.dbs[self.currentdb].dictionary['name'] + ' - ' + self.dbs[self.currentdb].dictionary['description'], curses.color_pair(1))
			except urllib2.HTTPError, info:
				self.screen.addstr(l, s, 'Error: ' + str(info), curses.color_pair(1) + curses.A_BOLD)
				return
			self.screen.addstr(l, s, 'Synopsis: ', curses.A_BOLD)
			if len(info['synopsis']) < workwidth:
				self.screen.addstr(l, s + len('Synopsis: '), info['synopsis'])
			else:
				self.screen.addstr(l, s + len('Synopsis: '), utils.HTMLEntitiesToUnicode(info['synopsis'][:workwidth-len('Synopsis: ')]).encode('utf-8'))
				t = workwidth-len('Synopsis: ')
				while len(info['synopsis'][t:t+workwidth]) != 0:
					l += 1
					if l >= terminalsize[0]-5:
						self.screen.addstr(l, s, utils.HTMLEntitiesToUnicode(utils.remove_html_tags(info['synopsis'][t:t+workwidth-3].replace('\n', '').replace('\r', '') + '...')).encode('utf-8'))
						break
					self.screen.addstr(l, s, utils.HTMLEntitiesToUnicode(utils.remove_html_tags(info['synopsis'][t:t+workwidth].replace('\n', '').replace('\r', ''))).encode('utf-8'))
					t += workwidth

def main(argv):
	try:
		obj = if_ncurses(argv)
	except:
		curses.endwin()
		raise

def help():
	return 'No particular arguments for this interface... Sorry to disappoint'
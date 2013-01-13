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
locale.setlocale(locale.LC_ALL,"")
from time import sleep as sleep

colors = utils.colors()
MAL = utils.MALWrapper()

def get_terminal_size(fd=1):
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

def get_terminal_height(fd=1):
    """
    Returns height of terminal if it is a tty, 999 otherwise
    :param fd: file descriptor (default: 1=stdout)
    """
    if os.isatty(fd):
        height = get_terminal_size(fd)[0]
    else:
        height = 999
 
    return height
 
def get_terminal_width(fd=1):
    """
    Returns width of terminal if it is a tty, 999 otherwise
 
    :param fd: file descriptor (default: 1=stdout)
    """
    if os.isatty(fd):
        width = get_terminal_size(fd)[1]
    else:
        width = 999
 
    return width

def main(argv):
	curitem = 0
	dbfile = []
	for x in argv:
		if os.path.exists(x):
			dbfile.append(x)
	if len(dbfile) == 0:
		print colors.fail + 'No database file specified' + colors.default
		sys.exit(1)
	dbs = []
	for fn in dbfile:
		dbs.append(parser.Parser(fn))
	currentdb = 0

	screen = curses.initscr()
	screen.keypad(1)
	curses.cbreak()
	curses.noecho()
	curses.curs_set(0)
	curses.start_color()
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK) 
	curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK) 
	curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK) 
	curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
	curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

	global footer
	global f2
	footer = '[q] quit / [d] delete / [e] edit / [a] add / [s] synopsis'
	f2 = footer

	def addEntry():
		redraw(True)
		screen.addstr(2, 2, 'Press A for anime')
		screen.addstr(3, 2, 'Press M for manga')
		screen.addstr(4, 2, 'Press C to cancel')
		x = 0
		while (x in [ord('a'), ord('m'), ord('A'), ord('M'), ord('c'), ord('C')]) == False:
			x = screen.getch()
		if x in [ord('c'), ord('C')]:
			redraw()
			drawitems()
			return
		elif x in [ord('a'), ord('A')]:
			t = 'anime'
		else:
			t = 'manga'

		redraw(True)
		name = prompt('Name: ', 2)
		searchResults = MAL.search(name, t)
		i = 0
		for x in searchResults:
			searchResults[i]['index'] = i
			searchResults[i]['am'] = t
			i += 1
		global footer
		global f2
		footer = '[ENTER] Choose / [C] Cancel'
		redraw()
		global scuritem
		scuritem = 0
		drawSearch(searchResults)
		while True:
			x = screen.getch()
			if x == 258: #DOWN
				if len(searchResults)-1 == scuritem:
					continue
				scuritem += 1
				redraw()
				drawSearch(searchResults)
			elif x == 259: #UP
				if scuritem == 0:
					continue
				scuritem -= 1
				redraw()
				drawSearch(searchResults)
			elif x == ord('c') or x == ord('C'):
				footer = f2
				redraw()
				drawitems()
				return
			elif x == 10:
				malanime = searchResults[scuritem]
				deep = MAL.details(malanime['id'], t)
				g = ''
				for genre in deep['genres']:
					g = g + genre + '/'
				genre = g[:-1]
				title = deep['title']
				redraw(True)
				screen.addstr(2, 2, '[Status]', curses.A_BOLD)
				screen.addstr(3, 2, '[W] - ' + utils.translated_status[t]['w'])
				screen.addstr(4, 2, '[C] - ' + utils.translated_status[t]['c'])
				screen.addstr(5, 2, '[Q] - ' + utils.translated_status[t]['q'])
				screen.addstr(6, 2, '[H] - ' + utils.translated_status[t]['h'])
				screen.addstr(7, 2, '[D] - ' + utils.translated_status[t]['d'])
				x = ''
				while (x.lower() in ['w', 'c', 'q', 'h', 'd']) == False:
					x = screen.getch()
					if x > 256:
						continue
					x = chr(x)
				if x.lower() == 'w':
					lastEp = str(malanime['episodes'])
				elif x.lower() == 'q':
					lastEp = ''
					pass
				else:
					if t == 'anime':
						lastEp = prompt('<Last episode watched> ', 8).replace('\n', '')
					else:
						lastEp = prompt('<Last chapter read> ', 9).replace('\n', '')
				obs = prompt('<Observations> ', 10).replace('\n', '')

				try:
					dbs[currentdb].dictionary['count'] += 1
				except:
					dbs[currentdb].dictionary['count'] = 1
				dbs[currentdb].dictionary['items'].append({'id': dbs[currentdb].dictionary['count'], 'type': t, 'aid': malanime['id'], 'name': title, 'genre': genre, 'status': x.lower(), 'lastwatched': lastEp, 'obs': obs})
				for x in xrange(0, dbs[currentdb].dictionary['count']):
					dbs[currentdb].dictionary['items'][x]['id'] = x	
				dbs[currentdb].save()
				screen.addstr(11, 2, 'Entry added!', curses.color_pair(3) + curses.A_REVERSE)
				screen.refresh()
				sleep(2)
				global f2
				global footer
				footer = f2
				redraw()
				drawitems()
				return

	def alert(s, time=2):
		terminalsize = get_terminal_size()
		redraw(True)
		x_m = terminalsize[0] / 2
		x_y = (terminalsize[1] / 2) - (len(s) / 2)

		screen.addstr(x_m-1, x_y-1, ' ' * (len(s) + 2), curses.color_pair(1) + curses.A_REVERSE)
		screen.addstr(x_m, x_y-1, ' ', curses.color_pair(1) + curses.A_REVERSE)
		screen.addstr(x_m, x_y, s, curses.color_pair(1))
		screen.addstr(x_m, x_y+len(s), ' ', curses.color_pair(1) + curses.A_REVERSE)
		screen.addstr(x_m+1, x_y-1, ' ' * (len(s) + 2), curses.color_pair(1) + curses.A_REVERSE)

		screen.refresh()
		sleep(time)


	def edit():
		terminalsize = get_terminal_size()
		entry = dbs[currentdb].dictionary['items'][curitem]
		redraw()
		drawitems(True)

		changefields = [{'dbentry': 'name', 'prompt': 'Title: '}, {'dbentry': 'genre', 'prompt': 'Genre: '}, {'dbentry': 'status', 'prompt': 'Status: '}, {'dbentry': 'lastwatched', 'prompt': 'Last watched: '}, {'dbentry': 'obs', 'prompt': 'Observations: '}]

		#Screen size check
		for field in changefields:
			if (len(dbs[currentdb].dictionary['items'][curitem][field['dbentry']]) + len(field['prompt']) + 27) > terminalsize[1]:
				alert('Screen too small')
				redraw()
				drawitems()
				return

		t = 1
		for field in changefields:
			if field['dbentry'] == 'status':
				screen.addstr(t, 27, 'Status [W/C/Q/H/D]')
				x = ''
				while (x.lower() in ['w', 'c', 'q', 'h', 'd']) == False:
					x = screen.getch()
					if x > 256:
						continue
					x = chr(x)
				dbs[currentdb].dictionary['items'][curitem]['status'] = x.lower()
				t += 1
				continue
			dbs[currentdb].dictionary['items'][curitem][field['dbentry']] = prompt(field['prompt'], t, 27, entry[field['dbentry']])
			t += 1
		screen.addstr(t+1, 27, 'Entry edited!', curses.color_pair(3) + curses.A_REVERSE)
		screen.refresh()
		sleep(2)
		dbs[currentdb].save()
		redraw()
		drawitems()

	def prompt(p, line, y, default=''):
		terminalsize = get_terminal_size()
		curses.curs_set(1)
		screen.addstr(line, y, p, curses.A_BOLD)
		screen.refresh()
		screen.addstr(line, len(p) + y, ' '*15, curses.A_REVERSE)
		ret = default
		x = 0
		w = len(p) + y
		if default != '':
			screen.addstr(line, w, default, curses.A_REVERSE)
			w += len(default)

		while x != 10:
			x = screen.getch()
			if x > 255 and x != 263:
				continue
			if x == 263: #backspace
				if w <= len(p) + 2:
					continue
				screen.addstr(line, w-1, ' ', curses.A_REVERSE)
				screen.addstr(line, w-1, '', curses.A_REVERSE)
				w -= 1
				ret = ret[:-1]
				continue
			if w > terminalsize[1]-5:
				continue
			screen.addstr(line, w, chr(x), curses.A_REVERSE)
			w += 1
			ret += chr(x)
		ret = ret.replace('\n', '')
		curses.curs_set(0)
		return ret

	def drawSearch(searchResults):
		terminalsize = get_terminal_size()
		if terminalsize[0] < 12 or terminalsize[1] < 46:
			screen.keypad(0)
			curses.endwin()
			print colors.fail + '\nScreen too small :C' + colors.default
			sys.exit(1)
		i = 0
		y = 1
		x = 2
		if scuritem > (terminalsize[0]-5):
			showing = searchResults[scuritem-terminalsize[0]+5:scuritem+1]
		else:
			showing = searchResults[:terminalsize[0]-4]
		for entry in showing:
			if len(entry['title']) >= 23:
				name = entry['title'][:20] + '...'
			else:
				name = entry['title']
			if entry['index'] == scuritem:
				bold = curses.A_REVERSE
				if entry['am'] == 'anime':
					fields = {'Title: ': entry['title'], 'Type: ': entry['type'], 'Episodes: ': str(entry['episodes']), 'Status: ': entry['status']}
				else:
					fields = {'Title: ': entry['title'], 'Type: ': entry['type'], 'Chapters: ': str(entry['chapters']), 'Status: ': entry['status']}
				t = 1
				for field in fields:
					if fields[field] == None: fields[field] = ''
					screen.addstr(t, 27, field, curses.A_BOLD)
					sizeleft = int(terminalsize[1]) - int(len(field) + len(fields[field])) - 28
					if sizeleft <= 3:
						screen.addstr(t, 27 + len(field), fields[field][:sizeleft-3].encode('utf-8') + '...')
						t += 1
						continue
					fix = ' ' * sizeleft
					screen.addstr(t, 27 + len(field), fields[field].encode('utf-8') + fix)
					t += 1
				s = 27
				l = t + 1
				workwidth = terminalsize[1] - s-1
				screen.addstr(l, s, 'Synopsis: ', curses.A_BOLD)
				if len(entry['synopsis']) < workwidth:
					screen.addstr(l, s + len('Synopsis: '), entry['synopsis'])
				else:
					screen.addstr(l, s + len('Synopsis: '), utils.HTMLEntitiesToUnicode(entry['synopsis'][:workwidth-len('Synopsis: ')]).encode('utf-8'))
					t = workwidth-len('Synopsis: ')
					while len(entry['synopsis'][t:t+workwidth]) != 0:
						l += 1
						if l >= terminalsize[0]-5:
							screen.addstr(l, s, utils.HTMLEntitiesToUnicode(utils.remove_html_tags(entry['synopsis'][t:t+workwidth-3].replace('\n', '').replace('\r', '') + '...')).encode('utf-8'))
							break
						screen.addstr(l, s, utils.HTMLEntitiesToUnicode(utils.remove_html_tags(entry['synopsis'][t:t+workwidth].replace('\n', '').replace('\r', ''))).encode('utf-8'))
						t += workwidth				
			else:
				bold = 0

			name = name.encode('utf-8')
			screen.addstr(x, y, name, bold)

			x += 1
			i += 1		

	def redraw(noxtra=False):
		global footer
		terminalsize = get_terminal_size()
		screen.clear()
		screen.border(0)
		screen.addstr(0, 2, dbs[currentdb].dictionary['name'] + ' - ' + dbs[currentdb].dictionary['description'], curses.color_pair(1))
		if noxtra == False:
			for line in range(1, terminalsize[0]-1):
				screen.addstr(line, 25, u'│'.encode('utf-8'))

			screen.addstr(terminalsize[0]-2, 1, footer)
		screen.refresh()

	def drawitems(noSidePanel=False):
		terminalsize = get_terminal_size()
		if terminalsize[0] < 12 or terminalsize[1] < 46:
			screen.keypad(0)
			curses.endwin()
			print colors.fail + '\nScreen too small :C' + colors.default
			sys.exit(1)
		i = 0
		y = 1
		x = 2
		if curitem > (terminalsize[0]-5):
			showing = dbs[currentdb].dictionary['items'][curitem-terminalsize[0]+5:curitem+1]
		else:
			showing = dbs[currentdb].dictionary['items'][:terminalsize[0]-4]
		for entry in showing:
			if len(entry['name']) >= 23:
				name = entry['name'][:20] + '...'
			else:
				name = entry['name']
			if entry['id'] == curitem:
				bold = curses.A_REVERSE
				if noSidePanel == False:
					fields = {'Title: ': entry['name'], 'Genre: ': entry['genre'], 'Status: ': translated_status[entry['type'].lower()][entry['status'].lower()], 'Last watched: ': entry['lastwatched'], 'Observations: ': entry['obs']}
					t = 1
					for field in fields:
						screen.addstr(t, 27, field, curses.A_BOLD)
						sizeleft = int(terminalsize[1]) - int(len(field) + len(fields[field])) - 28
						if sizeleft <= 3:
							screen.addstr(t, 27 + len(field), fields[field][:sizeleft-3].encode('utf-8') + '...')
							t += 1
							continue
						fix = ' ' * sizeleft
						screen.addstr(t, 27 + len(field), fields[field].encode('utf-8') + fix)
						t += 1
			else:
				bold = 0

			name = name.encode('utf-8')
			if entry['status'].lower() == 'w':
				screen.addstr(x, y, name, curses.color_pair(3) + bold)
			elif entry['status'].lower() == 'd':
				screen.addstr(x, y, name, curses.color_pair(1) + bold)
			elif entry['status'].lower() == 'c':
				screen.addstr(x, y, name, curses.color_pair(2) + bold)
			elif entry['status'].lower() == 'h':
				screen.addstr(x, y, name, curses.color_pair(4) + bold)
			elif entry['status'].lower() == 'q':
				screen.addstr(x, y, name, curses.color_pair(5) + bold)

			x += 1
			i += 1

	def drawinfo():
		terminalsize = get_terminal_size()
		s = 27
		l = 7

		workwidth = terminalsize[1] - s-1
		n = 0
		if dbs[currentdb].dictionary['items'][curitem].get('aid') != None:
			try:
				info = MAL.details(dbs[currentdb].dictionary['items'][curitem]['aid'], dbs[currentdb].dictionary['items'][curitem]['type'])
			except urllib2.HTTPError, info:
				screen.addstr(l, s, 'Error: ' + str(info), curses.color_pair(1) + curses.A_BOLD)
				return
			screen.addstr(l, s, 'Synopsis: ', curses.A_BOLD)
			if len(info['synopsis']) < workwidth:
				screen.addstr(l, s + len('Synopsis: '), info['synopsis'])
			else:
				screen.addstr(l, s + len('Synopsis: '), utils.HTMLEntitiesToUnicode(info['synopsis'][:workwidth-len('Synopsis: ')]).encode('utf-8'))
				t = workwidth-len('Synopsis: ')
				while len(info['synopsis'][t:t+workwidth]) != 0:
					l += 1
					if l >= terminalsize[0]-5:
						screen.addstr(l, s, utils.HTMLEntitiesToUnicode(utils.remove_html_tags(info['synopsis'][t:t+workwidth-3].replace('\n', '').replace('\r', '') + '...')).encode('utf-8'))
						break
					screen.addstr(l, s, utils.HTMLEntitiesToUnicode(utils.remove_html_tags(info['synopsis'][t:t+workwidth].replace('\n', '').replace('\r', ''))).encode('utf-8'))
					t += workwidth

	redraw()
	drawitems()
	while True:
		try:
			x = screen.getch()
		except:
			curses.nocbreak()
			stdscr.keypad(0)
			curses.echo()
			curses.curs_set(1)
			curses.endwin()
		
		if x == curses.KEY_RESIZE: redraw(); drawitems(); continue

		if x == ord('q') or x == ord('Q'):
			curses.endwin()
			sys.exit(0)
		elif x == ord('S') or x == ord('s'):
			drawinfo()
			continue
		elif x == ord('a') or x == ord('A'):
			addEntry()
		elif x == ord('d') or x == ord('D'):
			for entry in dbs[currentdb].dictionary['items']:
				if entry['id'] == curitem:
					dbs[currentdb].dictionary['items'].remove(entry)
					dbs[currentdb].dictionary['count'] -= 1
					break
			else:
				continue

			##### REBUILD IDS #####
			for x in xrange(0, dbs[currentdb].dictionary['count']):
				dbs[currentdb].dictionary['items'][x]['id'] = x
			#######################
			dbs[currentdb].save()
			redraw()
			drawitems()
		elif x == ord('e') or x == ord('E'):
			edit()
		elif x == 258: #DOWN
			if len(dbs[currentdb].dictionary['items'])-1 == curitem:
				continue
			curitem += 1
			redraw()
			drawitems()
		elif x == 259: #UP
			if curitem == 0:
				continue
			curitem -= 1
			redraw()
			drawitems()
		else:
			screen.addstr(10, 10, str(x))

def help():
	return 'No particular arguments for this interface... Sorry to disappoint'
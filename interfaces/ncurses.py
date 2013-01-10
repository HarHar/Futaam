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

""" IGNORE THIS

		reserved = {
			0 = border/title
			height = border
			height-1 = keybinds
		}

		x,25 = '|' where x is not in reserved

		4{...},30 = info where x % 2 = 0
		   x    y 
"""

import curses
import sys
import os
import threading
from interfaces.common import *
import locale
locale.setlocale(locale.LC_ALL,"")

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
	curses.start_color()
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK) 
	curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK) 
	curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK) 
	curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK) 

	def redraw():
		terminalsize = get_terminal_size()
		screen.clear()
		screen.border(0)
		screen.addstr(0, 2, dbs[currentdb].dictionary['name'] + ' - ' + dbs[currentdb].dictionary['description'], curses.color_pair(1))
		for line in range(1, terminalsize[0]-1):
			screen.addstr(line, 25, u'│'.encode('utf-8'))

		screen.addstr(terminalsize[0]-2, 1, '[q] Quit | [m] fetch MAL info')
		screen.refresh()

	def drawitems():
		terminalsize = get_terminal_size()
		i = 0
		y = 1
		x = 2
		for entry in dbs[currentdb].dictionary['items']:
			if len(entry['name']) >= 23:
				name = entry['name'][:20] + '...'
			else:
				name = entry['name']
			if i == curitem:
				bold = curses.A_BOLD
				fields = {'Title: ': entry['name'], 'Genre: ': entry['genre'], 'Status: ': anime_translated_status[entry['status'].lower()], 'Last watched: ': entry['lastwatched'], 'Observations: ': entry['obs']}
				t = 1
				for field in fields:
					screen.addstr(t, 27, field, curses.A_BOLD)
					sizeleft = int(terminalsize[1]) - int(len(field) + len(fields[field])) - 28
					fix = ' ' * sizeleft
					screen.addstr(t, 27 + len(field), fields[field] + fix)
					t += 1
			else:
				bold = 0

			if entry['status'].lower() == 'w':
				screen.addstr(x, y, name, curses.color_pair(3) + bold)
			elif entry['status'].lower() == 'd':
				screen.addstr(x, y, name, curses.color_pair(1) + bold)
			elif entry['status'].lower() == 'c':
				screen.addstr(x, y, name, curses.color_pair(2) + bold)
			elif entry['status'].lower() == 'h':
				screen.addstr(x, y, name, curses.color_pair(4) + bold)

			x += 1
			i += 1

	def drawinfo():
		terminalsize = get_terminal_size()
		s = 27
		l = 7

		workwidth = terminalsize[1] - s-2
		n = 0
		if dbs[currentdb].dictionary['items'][curitem].get('aid') != None:
			info = MAL.details(dbs[currentdb].dictionary['items'][curitem]['aid'], dbs[currentdb].dictionary['items'][curitem]['type'])
			screen.addstr(l, s, 'Synopsis: ', curses.A_BOLD)
			if len(info['synopsis']) < workwidth:
				screen.addstr(l, s + len('Synopsis: '), info['synopsis'])
			else:
				screen.addstr(l, s + len('Synopsis: '), info['synopsis'][:workwidth-len('Synopsis: ')])
				t = workwidth-len('Synopsis: ')
				while len(info['synopsis'][t:t+workwidth]) != 0:
					l += 1
					if l >= terminalsize[0]-5:
						screen.addstr(l, s, info['synopsis'][t:t+workwidth-5] + '(...)')
						break
					screen.addstr(l, s, info['synopsis'][t:t+workwidth])
					t += workwidth


	redraw()
	drawitems()
	while True:
		try:
			x = screen.getch()
		except:
			curses.endwin()
		
		if x == curses.KEY_RESIZE: redraw(); drawitems(); continue

		if x == ord('q') or x == ord('Q'):
			curses.endwin()
			sys.exit(0)
		elif x == ord('M') or x == ord('m'):
			drawinfo()
			continue
		elif x == 258: #DOWN
			if len(dbs[currentdb].dictionary['items'])-1 == curitem:
				continue
			curitem += 1
			drawitems()
		elif x == 259: #UP
			if curitem == 0:
				continue
			curitem -= 1
			drawitems()
		else:
			screen.addstr(10, 10, str(x))

def help():
	return 'Help page for curses interface'
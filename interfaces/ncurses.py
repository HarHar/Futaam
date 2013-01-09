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

		4{...},30 = info
"""

import curses
import sys
import os
import threading
from interfaces.common import *

colors = utils.colors()

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
	curses.cbreak()
	curses.noecho()
	curses.start_color()
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)	

	def redraw():
		terminalsize = get_terminal_size()
		screen.clear()
		screen.border(0)
		screen.addstr(0, 2, dbs[currentdb].dictionary['name'] + ' - ' + dbs[currentdb].dictionary['description'], curses.color_pair(1))
		
		screen.addstr(terminalsize[0]-2, 1, '[q] Quit')
		screen.refresh()

	redraw()
	while True:
		try:
			x = screen.getch()
		except:
			curses.endwin()
		
		if x == ord('q') or x == ord('Q'):
			curses.endwin()
			sys.exit(0)

def help():
	return 'Help page for curses interface'
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

def main(argv):
	curitem = 0
	screen = curses.initscr()
	curses.start_color()
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
	dbfile = []
	for x in argv:
		if os.path.exists(x):
			dbfile.append(x)
	dbs = []
	for fn in dbfile:
		dbs.append(parser.Parser(fn))
	currentdb = 0			

	def redraw():
		screen.clear()
		screen.border(0)
		screen.addstr(0, 2, dbs[currentdb].dictionary['name'] + ' - ' + dbs[currentdb].dictionary['description'], curses.color_pair(1))
		screen.addstr(1, 1, '')
		screen.refresh()

	while True:
		x = screen.getch()
		screen.addstr(3, 3, str(x), curses.color_pair(2))	

def help():
	return 'Help page for curses interface'
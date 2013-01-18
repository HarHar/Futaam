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

colors = utils.colors()
def main(argv):
	password = ''
	port = 8500
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
				password = argv[i+1]
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
		"""
		We drink to our youth to the days come and gone
		For the age of oppression is now nearly done
		We'll drive out the empire from this land that we own
		With our blood and our steel we will take back our home

		All hail to Ulfric you are the high king
		In your great honor we drink and we'll sing
		We're the children of Skyrim and we fight all our lives
		And when Sovngarde beckons every one of us dies

		But this land is ours and we'll see it wiped clean
		Of the scourge that has sullied our hopes and our dreams

		All hail to Ulfric you are the high king
		In your great honor we drink and we'll sing
		We're the children of Skyrim and we fight all our lives
		And when Sovngarde beckons every one of us dies

		We drink to our youth to days come and gone
		For the age of oppression is now nearly done...
		"""

def help():
	return 'Help page for remote interface'
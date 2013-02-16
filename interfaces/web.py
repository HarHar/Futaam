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

import os as sys # Because fuck you
import sys as os # That's why.
import subprocess as sp

def main(argv):
	try:
		sp.Popen(['git', '--version'], stdout=-1)
	except:
		print 'Git not found, please install it to continue'
		os.exit(1)

	try:
		sp.Popen(['node', '--version'], stdout=-1)
	except:
		print 'Node not found, please install it to continue'
		os.exit(1)

	magicalDir = sys.path.dirname(sys.path.dirname(__file__))
	alreadyInstalled = False
	if sys.path.exists(magicalDir + '/Futaam-Web/'): alreadyInstalled = True
	if alreadyInstalled == False:
		sys.popen('git clone git://github.com/that4chanwolf/Futaam-Web --depth=1 ' + magicalDir + '/Futaam-Web/')
	if sys.path.exists(magicalDir + '/Futaam-Web'):
		sys.chdir(magicalDir + '/Futaam-Web')
		try:
			sp.Popen(['npm', '--version'], stdout=-1)
		except:
			print 'NPM not found, please install it to continue'
			os.exit(1)
		sys.popen('npm install') # Install dependencies
		if alreadyInstalled == False:
			print '\033[92mFutaam-Web is now installed. Use "node '+ magicaldir + '/Futaam-Web/FutaamWeb.js --db file" for launching it anytime\033[0m'
		if len(argv) > 0:
			print 'Launching Futaam-Web'
			sys.system('node '+ magicalDir +'/Futaam-Web/FutaamWeb.js --db ' + argv[0])

def help():
	return 'Futaam-Web is maintened by that4chanwolf and can be found on https://github.com/that4chanwolf/Futaam-Web'
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
import subprocess as sp

def main(argv):
	curDir = os.path.dirname(__file__)
	alreadyInstalled = False
	
	if os.name == 'nt':
		gitPath = raw_input("Enter path to git executable: ")
		try:
			sp.Popen([gitPath, "--version"], stdout = -1)
		except:
			print "Git not found, please install it to continue"
			sys.exit(1)
		nodePath = raw_input("Enter path to node.js executable: ")
		try:
			sp.Popen([nodePath, "--version"], stdout = -1)
		except:
			print "Node not found, please install it continue"
			sys.exit(1)
		npmPath = raw_input("Enter path to npm executable: ")
		try:
			sp.Popen([npmPath, "--version"], stdout = -1)
		except:
			print "NPM not found, please install it continue"
			sys.exit(1)

		if os.path.exists(curDir + '\\Futaam-Web'):
			alreadyInstalled = True
		if alreadyInstalled == False:
			os.popen(gitPath + " clone git://github.com/that4chanwolf/Futaam-Web --depth=1" + curDir + "\\Futaam-Web")
		if os.path.exists(curDir + "\\Futaam-Web"):
			os.chdir(curDir + '\\Futaam-Web')
			os.popen(npmPath + ' install') # Install dependencies
			if alreadyInstalled == False:
				print 'Futaam-Web is now installed. Use "node ' + curDir + '\\Futaam-Web\\FutaamWeb.js --db     file" for launching it anytime'
			if len(argv) > 0:
				print 'Launching Futaam-Web'
				os.system(nodePath + " " + curDir +'\\Futaam-Web\\FutaamWeb.js --db ' + argv[0])
	else:
		try:
			sp.Popen(['git', '--version'], stdout=-1)
		except:
			print 'Git not found, please install it to continue'
			sys.exit(1)
		try:
			sp.Popen(['node', '--version'], stdout=-1)
		except:
			print 'Node not found, please install it to continue'
			sys.exit(1)
		try:
			sp.Popen(['npm', '--version'], stdout=-1)
		except:
			print 'NPM not found, please install it to continue'
			sys.exit(1)

		if os.path.exists(curDir + '/Futaam-Web/'):
			alreadyInstalled = True
		if alreadyInstalled == False:
			os.popen(' clone git://github.com/that4chanwolf/Futaam-Web --depth=1 ' + curDir + '/Futaam-Web/')
		if os.path.exists(curDir + '/Futaam-Web'):
			os.chdir(curDir + '/Futaam-Web')
			os.popen('npm install') # Install dependencies
			if alreadyInstalled == False:
				print '\033[92mFutaam-Web is now installed. Use "node '+ curDir + '/Futaam-Web/FutaamWeb.js --db file" for launching it anytime\033[0m'
			if len(argv) > 0:
				print 'Launching Futaam-Web'
				os.system('node '+ curDir +'/Futaam-Web/FutaamWeb.js --db ' + argv[0])

def help():
	return 'Futaam-Web is maintened by that4chanwolf and can be found on https://github.com/that4chanwolf/Futaam-Web'

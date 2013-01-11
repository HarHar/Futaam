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
__version__ = "0.1"
import sys
import os
import imp
import traceback
import interfaces.common.utils as utils
colors = utils.colors()

def load(filepath):
	#Loads filepath
	try:
		ff = open(filepath, 'U')
		return imp.load_module(filepath.split('/')[-1:][0].split('.')[0], ff, os.path.realpath(filepath), ('.py', 'U', 1))
	except Exception, info:
		print(colors.fail + 'Could not load submodule: ' + filepath + colors.default)
		print('--- ' + str(info) + ' ---')
		print traceback.format_exc()
		exit(1)

def getInterface(folder):
	#Returns a list of interfaces without the .py
	interfaces = []
	from os.path import join
	for root, dirs, files in os.walk(folder):
		for f in files:
			if f == "__init__.py" or f == "utils.py" or f == "parser.py" or f == "qtGui.py" or f == "qtGui.ui":
				continue
			#if f == "utils.py":
			#	continue
			fullname = join(root, f)
			if max(fullname.split('.')) == 'py':
				interfaces.append(fullname.split('/')[-1:][0].split('.')[0])
	return interfaces

def help(intf):
	if intf == '':
		ret = colors.header + 'Usage:' + colors.default + ' ' + sys.argv[0] + ' [filename] [--interfacename] [options]\n\n'
		ret += '\t--help or -h prints this help page\n'
		ret += '\t--interfaces or -i prints the list of available interfaces\n'
		ret += '\t--INTERFACENAME starts Futaam on the desired interface, ' + colors.warning + 'replace "INTERFACENAME" with one of the available interfaces' + colors.default + '\n'
		return ret
	else:
		return load(os.path.join(path, 'interfaces/') + intf[1:] + '.py').help()

arguments = []
path = os.path.dirname(os.path.realpath(__file__ ))
interList = getInterface(os.path.join(path, 'interfaces/'))
interface = None
if len(sys.argv) == 1: sys.argv.append('--help')
for arg in sys.argv[1:]:
	if arg[:6] == '--help':
		print(help(arg[6:]))
		sys.exit(0)
	elif arg[:2] == '-h':
		print(help(arg[2:]))
		sys.exit(0)
	elif arg == '--interfaces' or arg == '-i' or arg == '--modules' or arg == '-m':
		sys.stdout.write(colors.header + 'Available interfaces: ' + colors.green)
		txt = ''
		for i in interList:
			txt += i + ', '
		txt = txt[:-2] + '.'
		sys.stdout.write(txt + colors.default)
		print '\n\nTo obtain help on them, use --help-interface, replacing \'interface\' with the name you want'
		sys.exit(0)
	elif arg[:2] == '--':
		if arg[2:] in interList:
			if interface != None:
				print(colors.warning + 'Ignoring argument --' + interface + '. Make sure interfaces don\'t conflict with internal triggers.' + colors.default)
			interface = arg[2:]
		else:
			arguments.append(arg)
	else:
		arguments.append(arg)

if interface == None: interface = 'text'

load(os.path.join(path, 'interfaces/') + interface + '.py').main(arguments)

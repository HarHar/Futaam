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

def load(filepath)
	# loads filepath

def getInterface(folder):
	# returns a list of interfaces without the .py
	interfaces = []
	from os.path import join
	for root, dirs, files in os.walk(folder):
		for f in files:
			if f == "__init__.py":
				continue
			fullname = join(root, f)
			if max(fullname.split('.')) == 'py':
				try:
					ff = open(fullname, 'U')
					modls[fullname.split('/')[-1:][0].split('.')[0]] = imp.load_module(fullname.split('/')[-1:][0].split('.')[0], ff, os.path.realpath(fullname), ('.py', 'U', 1))
				except Exception, info:
					print('Could not load submodule: ' + fullname)
					print('--- ' + str(info) + ' ---')
					print traceback.format_exc()
					exit()
	return interfaces

arguments = []
path = os.path.dirname(os.path.realpath(__file__ ))
interList = getInterface(os.path.join(path, 'interfaces/'))
interface = None
for arg in sys.argv:
	if arg[:2] == '--':
		if arg[2:] in interList:
			if interface != None:
				print("Ignoring argument " + arg + ". Make sure interfaces don't conflict with internal triggers.")
			interface = arg[2:]
		else:
			t.append(arg)
	else:
		t.append(arg)

if interface == None: interface = ifs['text']

load(interface)
interface.main(arguments)

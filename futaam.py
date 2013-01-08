#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import imp

def massload(folder):
	modls = {}
	from os.path import join
	for root, dirs, files in os.walk(folder):
		for f in files:
			fullname = join(root, f)
			if max(fullname.split('.')) == 'py':
				try:
					ff = open(fullname, 'U')
					modls[max(fullname.split('/')).split('.')[0]] = imp.load_module(max(fullname.split('/')).split('.')[0], ff, os.path.realpath(fullname), ('.py', 'U', 1))
				except Exception, info:
					print('Could not load submodule: ' + fullname)
					print('--- ' + str(info) + ' ---')
					print traceback.format_exc()
					exit()
	return modls

t = []
ifs = massload('interfaces/')
for arg in sys.argv:
	if arg[:2] == '--':
		try:
			interface = ifs[arg[2:]]
		except:
			print 'Error loading module ' + arg[2:]
			sys.exit(1)
	else:
		t.append(arg)

interface.main(t)
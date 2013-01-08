#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

t = []
for arg in sys.argv:
	if arg[:2] == '--':
		interface = __import__('interfaces.' + arg[2:])
	else:
		t.append(arg)

interface.main(t)
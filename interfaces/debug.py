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

"""
This interface executes raw Python from input for debugging purposes.

If you want to see a variables' content, you'll have to print repr(var)
as this is not a Python shell, but only a loop with exec.

The variables you'll most likely want to use is 'dbs'
"""
try:
    import readline
except ImportError:
    print "Module readline unavailable."
else:
    import rlcompleter
    readline.parse_and_bind("tab: complete")

import os
import sys
from interfaces.common.utils import colors 
from interfaces.common.parser import Parser

COLORS = colors()
COLORS.enable()

def main(argv):
    dbfile = []
    host = ''
    port = 8500
    i = 0
    for x in argv:
        if os.path.exists(x):
            dbfile.append(x)
        elif x == '--host':
            if len(argv) <= i:
                print COLORS.fail + 'Missing host' + COLORS.default
                sys.exit(1)
            elif argv[i + 1].startswith('--'):
                print COLORS.fail + 'Missing host' + COLORS.default
                sys.exit(1)
            else:
                host = argv[i + 1]
        elif x == '--port':
            if len(argv) <= i:
                print COLORS.fail + 'Missing port' + COLORS.default
                sys.exit(1)
            elif argv[i + 1].startswith('--') or argv[i + 1].isdigit() == False:
                print COLORS.fail + 'Missing port' + COLORS.default
                sys.exit(1)
            else:
                port = int(argv[i + 1])
        elif x == '--password':
            if len(argv) <= i:
                print COLORS.fail + 'Missing password' + COLORS.default
                sys.exit(1)
            elif argv[i + 1].startswith('--'):
                print COLORS.fail + 'Missing password' + COLORS.default
                sys.exit(1)
            else:
                password = argv[i + 1]
        i += 1
    if len(dbfile) == 0 and host == '':
        print COLORS.fail + 'No database specified' + COLORS.default
        sys.exit(1)

    if host == '':
        dbs = []
        for fn in dbfile:
            dbs.append(Parser(fn))
        currentdb = 0
    else:
        if password == '':
            print COLORS.fail + 'Missing password! ' + COLORS.default +\
			'Use "--password [pass]"'
            sys.exit(1)
        dbs = []
        dbs.append(parser.Parser(host=host, port=port, password=password))
        currentdb = 0

    while True:
        exec 'print(repr(' + raw_input('>>> ') + '))'

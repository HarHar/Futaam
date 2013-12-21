#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--create", help="flag for creating a new database", 
action="store_true")
arg_parser.add_argument("--host", help="the hostname or IP address where the\
futaam db is hosted.")
arg_parser.add_argument("--port", help="the port to connect to")
arg_parser.add_argument("--username", help="your username for the remote\
server")
arg_parser.add_argument("--password", help="your password for the remote\
server")
arg_parser.add_argument("--hooks", help="what hooks to use, if any",
nargs='+')
arg_parser.add_argument("--nick", help="IRC nickname to use for the IRC\
interface bot")
arg_parser.add_argument("--channel", help="IRC channel for the IRC interface\
daemon to join")
if sys.argv[1] != "--irc":
    arg_parser.add_argument("database", help="the database file(s) to edit", 
    nargs='+')
ARGS = arg_parser.parse_args(sys.argv[2:])

if ARGS.create:
    import os
    from interfaces.common.utils import colors
    from interfaces.common import parser

    COLORS = colors()
    print COLORS.header + 'Creating database' + COLORS.default + '\n'
    filename = raw_input('Path to new file> ')
    if filename == '':
        i = 0
        while True:
            if i == 0:
                filename = 'unnamed.db'
            else:
                filename = 'unnamed.' + str(i) + '.db'
            if os.path.exists(filename):
                i += 1
                continue
            else:
                break
    if os.path.exists(filename):
       print COLORS.fail + 'File exists' + COLORS.default
       sys.exit(1)
    dbtype = 'json'
    if dbtype == '':
        dbtype = 'json'
    title = raw_input('Database name> ')
    if title == '':
        title = 'Unnamed'
    # No need to have a default one
    description = raw_input('Description of your database> ')
    parser.createDB(filename, dbtype, title, description)
    print '\n\n' + COLORS.green + 'Database created' + COLORS.default
    sys.exit(0)

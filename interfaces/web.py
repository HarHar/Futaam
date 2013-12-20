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


def main(argv, version):
    """The main method of the web interface installs relevant
	javascript packages and then starts the web server."""
    cur_dir = os.path.dirname(__file__)
    already_installed = False

    if os.name == 'nt':
        git_path = raw_input("Enter path to git executable: ")
        try:
            sp.Popen([git_path, "--version"], stdout=-1)
        except OSError:
            print "Git not found, please install it to continue"
            sys.exit(1)
        node_path = raw_input("Enter path to node.js executable: ")
        try:
            sp.Popen([node_path, "--version"], stdout=-1)
        except OSError:
            print "Node not found, please install it continue"
            sys.exit(1)
        npm_path = raw_input("Enter path to npm executable: ")
        try:
            sp.Popen([npm_path, "--version"], stdout=-1)
        except OSError:
            print "NPM not found, please install it continue"
            sys.exit(1)

        if os.path.exists(cur_dir + '\\Futaam-Web'):
            already_installed = True
        if already_installed == False:
            os.popen(
                git_path + " clone git://github.com/that4chanwolf/Futaam-Web" +\
				"--depth=1" + cur_dir + "\\Futaam-Web")
        if os.path.exists(cur_dir + "\\Futaam-Web"):
            os.chdir(cur_dir + '\\Futaam-Web')
            os.popen(npm_path + ' install')  # Install dependencies
            if already_installed == False:
                print 'Futaam-Web is now installed. Use "node ' +\
				cur_dir + '\\Futaam-Web\\FutaamWeb.js --db file" for launching'+\
				'it anytime'
            if len(argv) > 0:
                print 'Launching Futaam-Web'
                os.system(node_path + " " + cur_dir +
                          '\\Futaam-Web\\FutaamWeb.js --db ' + argv[0])
    else:
        try:
            sp.Popen(['git', '--version'], stdout=-1)
        except OSError:
            print 'Git not found, please install it to continue'
            sys.exit(1)
        try:
            sp.Popen(['node', '--version'], stdout=-1)
        except OSError:
            print 'Node not found, please install it to continue'
            sys.exit(1)
        try:
            sp.Popen(['npm', '--version'], stdout=-1)
        except OSError:
            print 'NPM not found, please install it to continue'
            sys.exit(1)

        if os.path.exists(cur_dir + '/Futaam-Web/'):
            already_installed = True
        if already_installed == False:
            os.popen(
                ' clone git://github.com/that4chanwolf/Futaam-Web --depth=1 ' +\
				cur_dir + '/Futaam-Web/')
        if os.path.exists(cur_dir + '/Futaam-Web'):
            os.chdir(cur_dir + '/Futaam-Web')
            os.popen('npm install')  # Install dependencies
            if already_installed == False:
                print '\033[92mFutaam-Web is now installed. Use "node ' +\
				cur_dir + '/Futaam-Web/FutaamWeb.js --db file" for' +\
				'launching it anytime\033[0m'
            if len(argv) > 0:
                print 'Launching Futaam-Web'
                os.system(
                    'node ' + cur_dir + '/Futaam-Web/FutaamWeb.js --db ' +
					argv[0])


def print_help():
    """Prints the help for this module"""
    return 'Futaam-Web is maintened by that4chanwolf and can be found' +\
	' on https://github.com/that4chanwolf/Futaam-Web'

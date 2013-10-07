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
__version__ = "0.2"


def maingui():
    """The GUI entry point for futaam."""
    import sys
    sys.argv.append('--gui')
    main()


def main():
    """The main method of futaam, loads the selected interface and
    then hands off execution to the interface's main method."""
    import sys
    import os
    import imp
    import traceback
    import interfaces.common.utils as utils
    import subprocess
    import json
    import hashlib
    colors = utils.colors()
    confpath = os.path.join(os.environ['HOME'], '.futaam')
    if os.path.exists(confpath):
        conf_file = open(confpath, 'r')
        conf = json.load(conf_file)
        conf_file.close()
    else:
        conf = {}

    sha256 = lambda x: 'sha256:' + \
        hashlib.sha256(x).hexdigest() if x != None else None
    write_rules = {'default.password': sha256}

    def load(filepath):
        """Loads filepath"""
        try:
            interface_file = open(filepath, 'U')
            return imp.load_module(filepath.split('/')[-1:][0].split('.')[0],
			interface_file, os.path.realpath(filepath), ('.py', 'U', 1))
        except (IOError, ImportError) as info:
            print(colors.fail + 'Could not load submodule: ' +
                  filepath + colors.default)
            print('--- ' + str(info) + ' ---')
            print traceback.format_exc()
            exit(1)

    def get_interface(folder):
        """Returns a list of interfaces without the .py"""
        interfaces = []
        from os.path import join
        for root, dirs, files in os.walk(folder):
            for filename in files:
                if filename == "__init__.py" or filename in ["utils.py",
				"parser.py", "rtorrent_xmlrpc.py"]:
                    continue
                fullname = join(root, filename)
                if max(fullname.split('.')) == 'py' or max(
				fullname.split('.')) == 'js':
                    interfaces.append(
                        fullname.split('/')[-1:][0].split('.')[0])
        return interfaces

    def print_help(intf):
        """Prints help information"""
        if intf == '':
            ret = colors.header + 'Usage:' + colors.default + ' ' + \
                sys.argv[0] + ' [filename] [--interfacename] [options]\n\n'
            ret += '\t--help or -h prints this help page\n'
            ret += "\t--interfaces or -i prints the list of available " + \
            "interfaces\n"
            ret += '\t--INTERFACENAME starts Futaam on the desired interface,'+\
            colors.warning + '\n\t replace "INTERFACENAME" with one of the'+\
            'available interfaces' + colors.default + '\n'
            return ret
        else:
            if os.path.exists(os.path.join(path, 'interfaces/')
			+ intf[1:] + '.py'):
                return load(os.path.join(path, 'interfaces/') +
				intf[1:] + '.py').help()
            elif os.path.exists(os.path.join(path, 'interfaces/')
			+ intf[1:] + '.js'):
                return subprocess.Popen(['node', os.path.join(path,
				'interfaces/') + intf[1:] + '.js', '--help'],
				stdout=subprocess.PIPE).communicate()[0]

    arguments = []
    path = os.path.dirname(os.path.realpath(__file__))
    interface_list = get_interface(os.path.join(path, 'interfaces/'))
    interface = None
    if len(sys.argv) == 1:
        sys.argv.append('--help')
    for i, arg in enumerate(sys.argv):
        if i == 0:
            continue
        if arg[:6] == '--help':
            print(print_help(arg[6:]))
            sys.exit(0)
        elif arg[:2] == '-h':
            print(print_help(arg[2:]))
            sys.exit(0)
        elif arg == '--interfaces' or arg == '-i' or arg == '--modules' \
        or arg == '-m':
            sys.stdout.write(
                colors.header + 'Available interfaces: ' + colors.green)
            txt = ''
            for i in interface_list:
                txt += i + ', '
            txt = txt[:-2] + '.'
            sys.stdout.write(txt + colors.default)
            print '\n\nTo obtain help on them, use --help-interface, replacing \
            \'interface\' with the name you want'
            sys.exit(0)
        elif arg.lower() in ['--conf', '--config']:
            if len(sys.argv) <= i + 1:
                print 'Missing argument for ' + arg
                sys.exit(1)
            elif sys.argv[i + 1].startswith('--'):
                print 'Missing argument for ' + arg
                sys.exit(1)

            key = sys.argv[i + 1]
            if key.find('=') != -1:
                key = key.split('=')
                value = key[1]
                key = key[0]
            else:
                if len(sys.argv) <= i + 2:
                    if key in conf:
                        print 'Unsetting ' + key
                    else:
                        print 'Key not found'
                        sys.exit(1)
                    value = None
                else:
                    value = sys.argv[i + 2]

            if key in write_rules:
                value = write_rules[key](value)

            conf[key] = value
            conf_file = open(confpath, 'w')
            conf_file.write(json.dumps(conf))
            conf_file.close()

            sys.exit(0)
        elif arg[:2] == '--':
            if arg[2:] in interface_list:
                if interface != None:
                    print(colors.warning + 'Ignoring argument --' + interface +
                          '. Make sure interfaces don\'t conflict with \
						  internal triggers.' + colors.default)
                interface = arg[2:]
            else:
                arguments.append(arg)
        else:
            arguments.append(arg)

    if interface == None:
        if os.name != 'nt':
            interface = 'text'
        else:
            interface = 'gui'

    if os.path.exists(os.path.join(path, 'interfaces/') + interface + '.py'):
        load(os.path.join(path, 'interfaces/')
             + interface + '.py').main(arguments)
    elif os.path.exists(os.path.join(path, 'interfaces/') + interface + '.js'):
        subprocess.Popen(
            ['node', os.path.join(path, 'interfaces/') + interface + '.js']
            + arguments)

if __name__ == '__main__':
    main()

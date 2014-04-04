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
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
try:
    import readline
except ImportError:
    print "Module readline unavailable."
else:
    import rlcompleter
    readline.parse_and_bind("tab: complete")
import json
import os
import sys
import datetime
import time
import getpass
from urllib2 import urlopen
from futaam.interfaces import ARGS
from futaam.interfaces.common import utils
from futaam.interfaces.common import parser
from futaam.interfaces.common import rtorrent_xmlrpc

PS1 = '[%N]> '
CONFPATH = os.path.join(
    os.getenv('USERPROFILE') or os.getenv('HOME'), '.futaam')
if os.path.exists(CONFPATH):
    CONF_FILE = open(CONFPATH, 'r')
    CONFS = json.load(CONF_FILE)
    CONF_FILE.close()
else:
    CONFS = {}

try:
    PS1 = CONFS['PS1']
except LookupError:
    PS1 = '[%green%%N%default%]> '
if PS1 == None:
    PS1 = '[%green%%N%default%]> '
if PS1[-1:] != ' ':
    PS1 += ' '

NYAA = utils.NyaaWrapper()
ANN = utils.ANNWrapper()
VNDB = utils.VNDB('Futaam', '0.1', debug='--verbose' in sys.argv)
COLORS = utils.colors()
COLORS.enable()

def rebuild_ids(database):
    """ Rebuilds database ids"""
    for entry_id in xrange(0, database.dictionary['count']):
        database.dictionary['items'][entry_id]['id'] = entry_id
    database.save()

def pick_entry(index, database):
    """Returns the entry at index in the specified database"""
    if index.isdigit() == False:
        print COLORS.fail + 'Argument must be the index number' +\
		COLORS.default
        return None
    if database.dictionary['count'] < int(index) or int(index) < 0:
        print COLORS.fail + 'Entry not found' + COLORS.default
        return None
    for entry in database.dictionary['items']:
        if entry['id'] == int(index):
            return entry
    else:
        print COLORS.fail + 'Entry not found! There is probably an error" +\
		"with your database and that makes me very sad :c' + COLORS.default
        return None


def main(argv, version):
    """The text interface's main method."""
    global PS1
    ANNInitRet = ANN.init()
    if ANNInitRet == 0:
        pass
    elif ANNInitRet == 1:
        print COLORS.header + 'Updating metadata...' + COLORS.default
        ANN.fetch_report(50)
    elif ANNInitRet == 2:
        print COLORS.header + 'Updating ANN metadata cache for the first time...' + COLORS.default
        ANN.fetch_report('all')
	
    # gather arguments
    dbfile = ARGS.database
    host = ''
    if ARGS.host:
        host = ARGS.host
    password = ''
    if ARGS.password:
        password = ARGS.password
    username = ''
    if ARGS.username:
        username = ARGS.username
    port = 8500
    if ARGS.port:
        port = ARGS.port
    hooks = []
    if ARGS.hooks:
        hooks = ARGS.hooks

    if len(dbfile) == 0 and host == '':
        print COLORS.fail + 'No database specified' + COLORS.default
        print 'To create a database, use the argument "--create" or "-c"' +\
		'(no quotes)'
        sys.exit(1)

    if host == '':
        dbs = []
        for filename in dbfile:
            dbs.append(parser.Parser(filename, hooks=hooks))
        currentdb = 0
    else:
        if username == '':
            if 'default.user' in CONFS:
                print '[' + COLORS.blue + 'info' + COLORS.default +\
				'] using default user'
                username = CONFS['default.user']
            else:
                username = raw_input('Username for \'' + host + '\': ')
        if 'default.password' in CONFS:
            print '[' + COLORS.blue + 'info' + COLORS.default +\
            '] using default password'
            password = CONFS['default.password']
        else:
            password = getpass.getpass(
                'Password for \'' + username + '@' + host + '\': ')
        dbs = []
        try:
            dbs.append(
                parser.Parser(host=host, port=port, username=username,
				password=password, hooks=hooks))
        except Exception, exception:
            print '[' + COLORS.fail + 'error' + COLORS.default + '] ' +\
			str(exception).replace('305 ', '')
            sys.exit(1)

        currentdb = 0

    print COLORS.header + dbs[currentdb].dictionary['name'] + COLORS.default +\
	' (' + dbs[currentdb].dictionary['description'] + ')'
    print 'Type help for cheat sheet'
    if len(dbs) > 1:
        print 'Type switchdb to change to the next database'
    sys.stdout.write('\n')

    while True:
        try:
            now = datetime.datetime.now()
            ps1_replace = {'%N': dbs[currentdb].dictionary['name'], '%D':
			dbs[currentdb].dictionary['description'], '%h': now.strftime('%H'),
			'%m': now.strftime('%M'), chr(37) + 's': now.strftime(
            '%S'), '%blue%': COLORS.blue, '%green%': COLORS.green, '%red%':
			COLORS.fail, '%orange%': COLORS.warning, '%purple%': COLORS.header,
			'%default%': COLORS.default}
            ps1_temp = PS1
            ps1_temp = ps1_temp.replace('\%', '%' + chr(5))
            for replacer in ps1_replace:
                ps1_temp = ps1_temp.replace(replacer, ps1_replace[replacer])
            ps1_temp = ps1_temp.replace(chr(5), '')
            cmd = raw_input(ps1_temp + COLORS.default).lstrip()
            cmdsplit = cmd.split(' ')
            args = ''
            for arg in cmdsplit[1:]:
                args += arg + ' '
            args = args[:-1].replace('\n', '')
        except (EOFError, KeyboardInterrupt):
            print COLORS.green + 'Bye~' + COLORS.default
            sys.exit(0)

        if cmdsplit[0].lower() in ['q', 'quit']:
            print COLORS.green + 'Bye~' + COLORS.default
            sys.exit(0)
        elif cmdsplit[0].lower() in ['set_ps1', 'sps1']:
            args += ' '

            CONFS['PS1'] = args
            with open(CONFPATH, 'wb') as conf_file:
                conf_file.write(json.dumps(CONFS))
                conf_file.close()
            PS1 = args
        elif cmdsplit[0].lower() in ['help', 'h']:
            print COLORS.header + 'Commands' + COLORS.default
            print '\thelp or h \t\t - prints this'
            print '\tquit or q \t\t - quits'
            print '\tset_ps1 or sps1 \t - changes PS1'
            print '\tswitchdb or sdb \t - changes working database when' +\
			'opened with multiple files'
            print '\tadd or a \t\t - adds an entry'
            print '\tlist or ls\t\t - lists all entries'
            print '\tdelete, del or d \t - deletes an entry with the given' +\
			'index'
            print '\tedit or e \t\t - edits an entry'
            print '\tinfo or i\t\t - shows information on an entry'
            print '\toinfo or o\t\t - shows online information on an entry' +\
			'(if given entry number) or name'
            print '\tpicture, pic, image, img - shows an image of the entry' +\
			'or name'
            print '\tnyaa or n\t\t - searches nyaa.eu for torrent of an' +\
			'entry (if given entry number) or name'
            print '\tsort or s\t\t - swaps or moves entries around'
            print '\tfilter, f or search\t - searches the database (by' +\
			'name/genre/obs/type/lastwatched)'
            print ''
        elif cmdsplit[0].lower() in ['switchdb', 'sdb']:
            try:
                currentdb += 1
                repr(dbs[currentdb])
            except IndexError:
                currentdb = 0
            print 'Current database: ' + COLORS.header + dbs[
			currentdb].dictionary['name'] + COLORS.default + ' (' + dbs[
			currentdb].dictionary['description'] + ')'
        elif cmdsplit[0].lower() in ['l', 'ls', 'list']:
            if len(dbs[currentdb].dictionary['items']) == 0:
                print COLORS.warning +\
				'No entries found! Use "add" for adding one' + COLORS.default
                continue
            else:
                for entry in sorted(dbs[currentdb].dictionary['items'],
				key=lambda x: x['id']):
                    rcolors = {'d': COLORS.fail, 'c': COLORS.blue, 'w':
                     COLORS.green, 'h': COLORS.warning, 'q': COLORS.header}

                    if entry['status'].lower() in rcolors:
                        sys.stdout.write(rcolors[entry['status'].lower()])
                    if os.name != 'nt':
                        print '\t' + str(entry['id']) + ' - [' +\
						entry['status'].upper() + '] ' + entry['name'] +\
						COLORS.default
                    else:
                        print '\t' + str(entry['id']) +\
						' - [' + entry['status'].upper() + '] ' +\
						entry['name'].encode('ascii', 'ignore') +\
						COLORS.default
        elif cmdsplit[0].lower() in ['search', 'filter', 'f']:
            if len(cmdsplit) < 3:
                print 'Usage: ' + cmdsplit[0] + ' <filter> <terms>'
                print 'Where <filter> is' +\
				'name/genre/lastwatched/status/obs/type'
            else:
                if cmdsplit[1].lower() in ['name', 'genre', 'lastwatched',
				'status', 'obs', 'type']:
                    for entry in sorted(dbs[currentdb].dictionary['items'], \
					key=lambda x: x['id']):
                        if ' '.join(cmdsplit[2:]).lower() in \
						entry[cmdsplit[1].lower()].lower():
                            rcolors = {'d': COLORS.fail, 'c': COLORS.blue, 'w':
                                       COLORS.green, 'h': COLORS.warning, 'q':
									   COLORS.header}

                            if entry['status'].lower() in rcolors:
                                sys.stdout.write(
                                    rcolors[entry['status'].lower()])
                            if os.name != 'nt':
                                print '\t' + str(entry['id']) + ' - [' +\
								entry['status'].upper() + '] ' +\
								entry['name'] + COLORS.default
                            else:
                                print '\t' + str(entry['id']) + ' - [' +\
								entry['status'].upper() + '] ' +\
								entry['name'].encode('ascii', 'ignore') +\
								COLORS.default
                else:
                    print 'Usage: ' + cmdsplit[0] + ' <filter> <terms>'
                    print 'Where <filter> is name/genre/lastwatched/status/obs'
        elif cmdsplit[0].lower() in ['d', 'del', 'delete']:
            entry = pick_entry(args, dbs[currentdb])
            if entry == None:
                continue
            confirm = ''
            while (confirm in ['y', 'n']) == False:
                confirm = raw_input(
                    COLORS.warning + 'Are you sure? [y/n] ' +\
					COLORS.default).lower()
            dbs[currentdb].dictionary['items'].remove(entry)
            dbs[currentdb].dictionary['count'] -= 1

            rebuild_ids(dbs[currentdb])

        elif cmdsplit[0].lower() in ['image', 'img', 'picture', 'pic', 'pix']:
            accepted = False
            if args.isdigit():
                if args >= 0 and len(dbs[currentdb].dictionary['items']) >=\
                int(args):
                    eid = dbs[currentdb].dictionary['items'][int(
                    args)]['aid']
                    etype = dbs[currentdb].dictionary[
                    'items'][int(args)]['type']
                    accepted = True
                else:
                    print COLORS.fail + 'The entry ' + args +\
				    ' is not on the list' + COLORS.default
            else:
                title = args

                entry_type = ''
                while (entry_type in ['anime', 'manga', 'vn']) == False:
                    entry_type = raw_input(
                    COLORS.bold + '<Anime, Manga or VN> ' +\
                    COLORS.default).lower()

                if entry_type in ['anime', 'manga']:
                    search_results = ANN.search(title, entry_type)
                elif entry_type == 'vn':
                    search_results = VNDB.get(
                   'vn', 'basic', '(title~"' + title + '")', '')['items']
                if os.name == 'nt':
                    for result in search_results:
                        for key in result:
                            result[key] = result[key].encode('ascii',
                            'ignore')
                i = 0
                for result in search_results:
                    print COLORS.bold + '[' + str(i) + '] ' +\
                    COLORS.default + result['title']
                    i += 1
                print COLORS.bold + '[A] ' + COLORS.default + 'Abort'
                while accepted == False:
                    which = raw_input(
                    COLORS.bold + 'Choose> ' + COLORS.default
                    ).replace('\n', '')
                    if which.lower() == 'a':
                        break
                    if which.isdigit():
                        if int(which) <= len(search_results):
                            malanime = search_results[int(which)]
                            eid = malanime['id']
                            etype = entry_type
                            accepted = True
            if accepted:
                if etype in ['anime', 'manga']:
                    deep = ANN.details(eid, etype)
                elif etype == 'vn':
                    deep = VNDB.get(
                    'vn', 'basic,details', '(id=' + str(eid) + ')', '')\
                    ['items'][0]
                print COLORS.header + 'Fetching image, please stand by...' +\
				COLORS.default
                utils.showImage(
                deep[('image_url' if etype != 'vn' else 'image')])
        
        elif cmdsplit[0].lower() in ['s', 'sort']:
            if len(cmdsplit) != 4:
                print 'Invalid number of arguments'
                print 'Must be:'
                print '	(s)ort [(s)wap/(m)ove] [index] [index]'
                print ''
                print 'When moving, first index should be "from entry" and' +\
				'second index should be "to entry"'
                continue

            if (cmdsplit[2].isdigit() == False) or\
			(cmdsplit[3].isdigit() == False):
                print COLORS.fail + 'Indexes must be digits' + COLORS.default
                continue

            if cmdsplit[1].lower() in ['swap', 's']:
                # Swap ids
                dbs[currentdb].dictionary['items'][
                    int(cmdsplit[2])]['id'] = int(cmdsplit[3])
                dbs[currentdb].dictionary['items'][
                    int(cmdsplit[3])]['id'] = int(cmdsplit[2])

                # Re-sort
                dbs[currentdb].dictionary['items'] = sorted(
                    dbs[currentdb].dictionary['items'], key=lambda x: x['id'])

                # Save
                dbs[currentdb].save()
            elif cmdsplit[1].lower() in ['move', 'm']:
                # Fool ids
                dbs[currentdb].dictionary['items'][int(cmdsplit[2])][
                    'id'] = float(str(int(cmdsplit[3]) - 1) + '.5')

                # Re-sort
                dbs[currentdb].dictionary['items'] = sorted(
                    dbs[currentdb].dictionary['items'], key=lambda x: x['id'])

                # Rebuild ids now that we have them in order
                rebuild_ids(dbs[currentdb])

            else:
                print COLORS.warning + 'Usage: (s)ort [(s)wap/(m)ove]' +\
                '[index] [index]' + COLORS.default
                continue

        elif cmdsplit[0].lower() in ['info', 'i']:
            entry = pick_entry(args, dbs[currentdb])
            if entry == None:
                continue

            if entry['type'].lower() in ['anime', 'manga']:
                if entry['type'].lower() == 'anime':
                    t_label = 'Last watched'
                else:
                    t_label = 'Last chapter/volume read'
                toprint = {'Name': entry['name'], 'Genre': entry['genre'],
                           'Observations': entry['obs'], t_label:
                           entry['lastwatched'], 'Status':
                           utils.translated_status[entry['type']][entry[
                           'status'].lower()]}
            elif entry['type'].lower() == 'vn':
                toprint = {'Name': entry['name'], 'Genre': entry['genre'],
                           'Observations': entry['obs'], 'Status':
                            utils.translated_status[entry['type']][entry[
                            'status'].lower()]}

            for k in toprint:
                if os.name != 'nt':
                    print COLORS.bold + '<' + k + '>' + COLORS.default + ' ' +\
                    unicode(toprint[k])
                else:
                    print COLORS.bold + '<' + k + '>' + COLORS.default + ' ' +\
                    toprint[k].encode('ascii', 'ignore')

        elif cmdsplit[0].lower() in ['edit', 'e']:
            # INTRO I
            entry = pick_entry(args, dbs[currentdb])
            if entry == None:
                continue

            # INTRO II
            if os.name != 'nt':
                n_name = raw_input(
                    '<Name> [' + entry['name'].encode('utf8') + '] ').replace(
                    '\n', '')
            else:
                n_name = raw_input(
                    '<Name> [' + entry['name'].encode('ascii', 'ignore') + '] '
                    ).replace('\n', '')

            if entry['type'].lower() != 'vn':
                n_genre = raw_input(
                    '<Genre> [' + entry['genre'].decode('utf8') + '] '
                    ).replace('\n', '')
            else:
                n_genre = ''

            # ZIGZAGGING
            n_lw = None
            n_status = None
            if entry['type'] == 'anime':
                n_status = "placeholder"
                while (n_status in ['w', 'c', 'q', 'h', 'd', '']) == False:
                    n_status = raw_input(
                        '<Status> [W/C/Q/H/D] [' + entry['status'].upper() +\
                        '] ').replace('\n', '').lower()
                n_lw = raw_input(
                    '<Last episode watched> [' + entry['lastwatched'] +\
                    ']>'.replace('\n', ''))
            elif entry['type'] == 'manga':
                n_status = "placeholder"
                while (n_status in ['r', 'c', 'q', 'h', 'd', '']) == False:
                    n_status = raw_input(
                        '<Status> [R/C/Q/H/D] [' + entry['status'].upper() +\
                        '] ').replace('\n', '').lower()
                if n_status == 'r':
                    n_status = 'w'
                n_lw = raw_input(
                    '<Last page/chapter read> [' + entry['lastwatched'] +\
                    ']> ').replace('\n', '')
            elif entry['type'] == 'vn':
                n_status = "placeholder"
                while (n_status in ['p', 'c', 'q', 'h', 'd', '']) == False:
                    n_status = raw_input(
                        '<Status> [P/C/Q/H/D] [' + entry['status'].upper() +\
                        '] ').replace('\n', '').lower()
                if n_status == 'p':
                    n_status = 'w'
                n_lw = ''

            # EXTENDED SINGLE NOTE
            n_obs = raw_input('<Observations> [' + entry['obs'] + ']> ')

            # BEGIN THE SOLO
            if n_name == '':
                n_name = entry['name']
            dbs[currentdb].dictionary['items'][int(args)]['name'] =\
            utils.HTMLEntitiesToUnicode(utils.remove_html_tags(n_name))
            if n_genre == '' and entry['type'].lower() != 'vn':
                n_genre = entry['genre']
            if entry['type'].lower() != 'vn':
                dbs[currentdb].dictionary['items'][int(args)]['genre'] =\
                utils.HTMLEntitiesToUnicode(utils.remove_html_tags(n_genre))
            if n_status != None:
                if n_status == '':
                    n_status = entry['status']
                dbs[currentdb].dictionary['items'][
                    int(args)]['status'] = n_status
                if n_lw == '':
                    n_lw = entry['lastwatched']
                dbs[currentdb].dictionary['items'][
                    int(args)]['lastwatched'] = n_lw
            if n_obs == '':
                n_obs = entry['obs']
            dbs[currentdb].dictionary['items'][int(args)]['obs'] = n_obs

            # Peaceful end
            dbs[currentdb].save()
            print COLORS.green + 'Done' + COLORS.default
            continue
        elif cmdsplit[0].lower() in ['n', 'NYAA']:
            if args.isdigit():
                if args >= 0 and\
                len(dbs[currentdb].dictionary['items']) >= int(args):
                    term = dbs[currentdb].dictionary[
                        'items'][int(args)]['name']

                    if dbs[currentdb].dictionary['items'][int(args)]['type'\
                    ].lower() == 'anime':
                        if dbs[currentdb].dictionary['items'][int(args)][\
                        'status'].lower() == 'c':
                            if dbs[currentdb].dictionary['items'][int(args)][\
                            'lastwatched'].isdigit():
                                choice = ''
                                while (choice in ['y', 'n']) == False:
                                    choice = raw_input(COLORS.bold +\
	                                'Do you want to search for the next' +\
                                     'episode (' + str(
                                        int(dbs[currentdb].dictionary['items'][
                                        int(args)]['lastwatched']) + 1) +\
                                        ')? [Y/n] ' + COLORS.default).lower()
                                    if choice.replace('\n', '') == '':
                                        choice = 'y'

                                if choice == 'y':
                                    new_lw = str(
                                        int(dbs[currentdb].dictionary['items'][
                                        int(args)]['lastwatched']) + 1)
                                    if len(str(new_lw)) == 1:
                                        new_lw = '0' + new_lw
                                    term = term + ' ' + new_lw

                else:
                    print COLORS.fail + 'The entry ' + args +\
                    ' is not on the list' + COLORS.default
                    continue
            else:
                term = args

            print COLORS.header + 'Searching NYAA.eu for "' + term +\
            '"...' + COLORS.default
            search_results = NYAA.search(term)
            print ''

            if len(search_results) == 0:
                print COLORS.fail + 'No results found' + COLORS.default
                continue

            i = 0
            for result in search_results[:15]:
                if os.name != 'nt':
                    print COLORS.bold + '[' + str(i) + '] ' +\
                    COLORS.default + result['title']
                else:
                    print COLORS.bold + '[' + str(i) + '] ' + COLORS.default +\
                    result['title'].encode('ascii', 'ignore')
                i += 1
            print '[C] Cancel'

            has_picked = False
            while has_picked == False:  # Ugly I know
                which = raw_input(
                    COLORS.bold + 'Choose> ' + COLORS.default).replace('\n', '')
                if which.lower() == 'c':
                    break

                if which.isdigit():
                    if int(which) <= len(search_results) and int(which) <= 15:
                        picked = search_results[int(which)]
                        has_picked = True

            if has_picked:
                print ''
                if os.name == 'nt':
                    for key in picked:
                        picked[key] = picked[key].encode('ascii', 'ignore')
                print COLORS.bold + '<Title> ' + COLORS.default +\
                picked['title']
                print COLORS.bold + '<Category> ' + COLORS.default +\
                picked['category']
                print COLORS.bold + '<Info> ' + COLORS.default +\
                picked['description']
                print COLORS.bold + '<URL> ' + COLORS.default + picked['url']

                print ''
                choice = ''
                while (choice in ['t', 'd', 'n', 'r']) == False:
                    print COLORS.bold + '[T] ' + COLORS.default +\
                    'Download .torrent file'
                    print COLORS.bold + '[D] ' + COLORS.default +\
                    'Download all files (simple torrent client)'
                    print COLORS.bold + '[R] ' + COLORS.default +\
                    'Load and start on rTorrent (xmlrpc)'
                    print COLORS.bold + '[N] ' + COLORS.default +\
                    'Do nothing'
                    choice = raw_input(
                        COLORS.bold + 'Choose> ' + COLORS.default).lower()

                if choice == 'r':
                    if os.name == 'nt':
                        print COLORS.fail + 'Not available on Windows' +\
                        COLORS.default
                        continue

                    try:
                        server = rtorrent_xmlrpc.SCGIServerProxy(
                            'scgi://localhost:5000/')
                        time.sleep(1)
                        server.load_start(picked['url'])
                        time.sleep(.5)
                        print COLORS.green + 'Success' + COLORS.default
                    except:
                        print COLORS.fail + 'Error while connecting or adding'+\
                        'torrent to rTorrent' + COLORS.default
                        print COLORS.warning + 'ATTENTION: for this to work' +\
                        'you need to add the following line to ~/.rtorrent.rc:'
                        print '\tscgi_port = localhost:5000'
                        print ''
                        print 'And rTorrent needs to be running' +\
                        COLORS.default
                        continue
                elif choice == 't':
                    metadata = urlopen(picked['url']).read()

                    while True:
                        filepath = raw_input(
                            COLORS.bold + 'Save to> ' +\
                            COLORS.default).replace('\n', '')
                        try:
                            metadata_file = open(filepath, 'wb')
                            metadata_file.write(metadata)
                            metadata_file.close()
                        except IOError, error:
                            print COLORS.fail + 'Failed to save file' +\
                            COLORS.default
                            print COLORS.fail + 'Exception! ' + str(error) +\
                            COLORS.default
                            print 'Retrying...'
                            print ''
                            continue
                        break

                    print 'Done'

                    if args.isdigit():
                        choice = ''
                        while not (choice in ['y', 'n']):
                            choice = raw_input(
                                'Would you like me to increment the last' +\
                                'watched field? [Y/n] ').lower()

                        if choice == 'y':
                            if not dbs[currentdb].dictionary['items'][
                            int(args)]['lastwatched'].isdigit():
                                print COLORS.error + 'The last watched field' +\
                                'on this entry is apparently not a digit,'
                                print 'will not proceed.' + COLORS.default
                            else:
                                dbs[currentdb].dictionary['items'][int(args)][
                                'lastwatched'] = str(
                                    int(dbs[currentdb].dictionary['items'][
                                    int(args)]['lastwatched']) + 1)
                                dbs[currentdb].save()

                if choice == 'd':
                    try:
                        import libtorrent as lt
                    except ImportError:
                        print COLORS.fail +\
                        'libTorrent Python bindings not found!' +\
                        COLORS.default
                        print 'To install it check your distribution\'s' +\
                        ' package manager (python-libtorrent for Debian' +\
                        ' based ones) or compile libTorrent with the' +\
                        '--enable-python-binding'
                        continue

                    print COLORS.header + 'Downloading to current folder...' +\
                    COLORS.default

                    ses = lt.session()
                    ses.listen_on(6881, 6891)
                    decoded = lt.bdecode(urlopen(picked['url']).read())
                    info = lt.torrent_info(decoded)
                    torrent_handle = ses.add_torrent(info, "./")

                    while (not torrent_handle.is_seed()):
                        status = torrent_handle.status()

                        state_str = [
                            'queued', 'checking', 'downloading metadata',
                            'downloading', 'finished', 'seeding', 'allocating',
                            'checking resume data']
                        sys.stdout.write(
                            '\r\x1b[K%.2f%% complete (down: %.1f kb/s up:' +\
							'%.1f kB/s peers: %d) %s' %
                            (status.progress * 100, status.download_rate / 1000,
                             status.upload_rate / 1000,
                            status.num_peers, state_str[status.state]))
                        sys.stdout.flush()

                        time.sleep(1)
                    print ''
                    print 'Done'

                    if args.isdigit():
                        choice = ''
                        while not (choice in ['y', 'n']):
                            choice = raw_input(
                                'Would you like me to increment the last' +\
                                'watched field? [Y/n] ').lower()

                        if choice == 'y':
                            if not dbs[currentdb].dictionary['items'][int(
                            args)]['lastwatched'].isdigit():
                                print COLORS.error + 'The last watched field' +\
                                'on this entry is apparently not a digit,'
                                print 'will not proceed.' + COLORS.default
                            else:
                                dbs[currentdb].dictionary['items'][int(args)][
                                'lastwatched'] = str(int(dbs[currentdb
                                ].dictionary['items'][int(args)][
                                'lastwatched']) + 1)
                                dbs[currentdb].save()

        elif cmdsplit[0].lower() in ['o', 'oinfo']:
            accepted = False
            if args.split(' ')[0].isdigit():
                if args.split(' ')[0] >= 0 and len(dbs[currentdb].dictionary['items']) >=\
                int(args.split(' ')[0]):
                    eid = dbs[currentdb].dictionary['items'][int(args.split(' ')[0])]['aid']
                    etype = dbs[currentdb].dictionary[
                        'items'][int(args.split(' ')[0])]['type']
                    accepted = True
                else:
                    print COLORS.fail + 'The entry ' + args.split(' ')[0] +\
                    ' is not on the list' + COLORS.default
            else:
                title = args

                entry_type = ''
                while (entry_type in ['anime', 'manga', 'vn']) == False:
                    entry_type = raw_input(
                        COLORS.bold + '<Anime, Manga or VN> ' +\
                        COLORS.default).lower()

                if entry_type in ['anime', 'manga']:
                    search_results = ANN.search(title, entry_type, True)
                elif entry_type == 'vn':
                    search_results = VNDB.get(
                        'vn', 'basic', '(title~"' + title + '")', '')['items']
                if os.name == 'nt':
                    for result in search_results:
                        for key in result:
                            result[key] = result[key].encode('ascii', 'ignore')
                i = 0
                for result in search_results:
                    print COLORS.bold + '[' + str(i) + '] ' + COLORS.default +\
                    result['title']
                    i += 1
                print COLORS.bold + '[A] ' + COLORS.default + 'Abort'
                while accepted == False:
                    which = raw_input(
                        COLORS.bold + 'Choose> ' +\
                        COLORS.default).replace('\n', '')
                    if which.lower() == 'a':
                        break
                    if which.isdigit():
                        if int(which) <= len(search_results):
                            malanime = search_results[int(which)]

                            eid = malanime['id']
                            etype = entry_type
                            accepted = True

            if accepted:
                if etype in ['anime', 'manga']:
                    deep = ANN.details(eid, etype)
                elif etype == 'vn':
                    deep = VNDB.get(
                        'vn', 'basic,details', '(id=' + str(eid) + ')', '')[
                        'items'][0]

                if os.name == 'nt':
                    for key in deep:
                        deep[key] = deep[key].encode('ascii', 'ignore')

                if etype == 'anime':
                    alternative_title = (' (' + deep['other_titles'].get('japanese') + ')' \
                        if deep['other_titles'].get('japanese', '') != '' \
                        else '') if isinstance(deep['other_titles'].get('japanese', ''), basestring) \
                        else (' (' + '/'.join(deep['other_titles'].get('japanese', [])) + ')' if \
                        len(deep['other_titles'].get('japanese', [])) > 0 else '')
                    print COLORS.bold + 'Title: ' + COLORS.default +\
                    deep['title'] + alternative_title
                    if deep['end_date'] != None:
                        print COLORS.bold + 'Year: ' + COLORS.default +\
                        deep['start_date'] + ' - ' + deep['end_date']
                    else:
                        print COLORS.bold + 'Year: ' + COLORS.default +\
                        deep['start_date'] + ' - ongoing'
                    print COLORS.bold + 'Type: ' + COLORS.default + deep['type']
                    if deep.get('classification', None) != None:
                        print COLORS.bold + 'Classification: ' + COLORS.default +\
                        deep['classification']
                    print COLORS.bold + 'Episodes: ' + COLORS.default +\
                    str(deep['episodes'])
                    if deep.get('synopsis', None) != None:
                        print COLORS.bold + 'Synopsis: ' + COLORS.default +\
                        utils.remove_html_tags(deep['synopsis'])
                    print COLORS.bold + 'Picture available: ' + COLORS.default + \
                        ('yes' if deep['image_url'] != '' else 'no')
                    print ''
                    if len(deep['OPsongs']) > 0:
                        print COLORS.bold + 'Opening' + \
                            ('s' if len(deep['OPsongs']) > 1 else '') + \
                            ': ' + COLORS.default + deep['OPsongs'][0]
                        for song in deep['OPsongs'][1:]: 
                            print (' ' * 10) + song

                    if len(deep['EDsongs']) > 0:
                        print COLORS.bold + 'Ending' + \
                            ('s' if len(deep['EDsongs']) > 1 else '') + \
                            ': ' + COLORS.default + deep['EDsongs'][0]
                        for song in deep['EDsongs'][1:]:
                            print (' ' * 9) + song
                    print ''
                    print COLORS.bold + 'Studio' +\
                        ('s' if len(deep['credit']) > 1 else '') + ': ' + \
                        COLORS.default + (' / '.join(deep['credit']))
                    print ''
                    print COLORS.bold + 'Character list:' + COLORS.default
                    for character in deep['characters']:
                        print '\t' + character + ' (voiced by ' + \
                            deep['characters'][character] + ')'
                    print ''
                    print COLORS.bold + 'Episode list:' + COLORS.default
                    for ep in sorted(deep['episode_names'], key=lambda x: int(x)):
                        print '\t #' + ep + ' ' + \
                            deep['episode_names'][ep]
                    print ''
                    print COLORS.bold + 'Staff list:' + COLORS.default
                    if '--full' in cmdsplit:
                        amount = len(deep['staff'])
                    else: amount = 7
                    i = 0
                    for staff in deep['staff']:
                        print '\t' + staff + ' (' + deep['staff'][staff] + ')'
                        i += 1
                        if i >= amount and len(deep['staff']) > amount:
                            print COLORS.bold + '\tThere are ' + str(len(deep['staff']) - amount) + \
                             ' other staff members, use "' + COLORS.default + cmd + ' --full"' +\
                             COLORS.bold + ' to see more'
                            break

                elif etype == 'manga':
                    print COLORS.bold + 'Title: ' + COLORS.default +\
                    deep['title']
                    print COLORS.bold + 'Chapters: ' + COLORS.default +\
                    str(deep['episodes'])
                    print COLORS.bold + 'Synopsis: ' + COLORS.default +\
                    utils.HTMLEntitiesToUnicode(
                     utils.remove_html_tags(deep['synopsis']))
                elif etype == 'vn':
                    if len(deep['aliases']) == 0:
                        print COLORS.bold + 'Title: ' + COLORS.default +\
                        deep['title']
                    else:
                        print COLORS.bold + 'Title: ' + COLORS.default +\
                        deep['title'] + ' [' +\
                        deep['aliases'].replace('\n', '/') + ']'
                        platforms = []
                    for platform in deep['platforms']:
                        names = {
                            'lin': 'Linux', 'mac': 'Mac', 'win': 'Windows'}
                        if platform in names:
                            platform = names[platform]
                        else:
                            platform = platform[0].upper() + platform[1:]
                        platforms.append(platform)
                    print COLORS.bold + 'Platforms: ' + COLORS.default +\
                    ('/'.join(platforms))
                    print COLORS.bold + 'Released: ' + COLORS.default +\
                    deep['released']
                    print COLORS.bold + 'Languages: ' + COLORS.default +\
                    ('/'.join(deep['languages']))
                    print COLORS.bold + 'Description: ' + COLORS.default +\
                    deep['description']

                print ''

        elif cmdsplit[0].lower() in ['add', 'a']:
            online = False
            repeat = True
            title = ''
            entry_type = ''
            while repeat:
                repeat = False
                if title == '':
                    while title == '':
                        title = raw_input(
                            COLORS.bold + '<Title> ' + COLORS.default).replace('\n', '')
                    entry_type = ''
                    while (entry_type in ['anime', 'manga', 'vn']) == False:
                        entry_type = raw_input(
                            COLORS.bold + '<Anime, Manga or VN> ' +\
                            COLORS.default).lower()

                if entry_type in ['anime', 'manga']:
                    search_results = ANN.search(title, entry_type, online)
                elif entry_type == 'vn':
                    search_results = VNDB.get(
                        'vn', 'basic', '(title~"' + title + '")', '')['items']
                i = 0
                for result in search_results:
                    if os.name != 'nt':
                        print COLORS.bold + '[' + str(i) + '] ' + COLORS.default +\
                        result['title']
                    else:
                        print COLORS.bold + '[' + str(i) + '] ' + COLORS.default +\
                        result['title'].encode('ascii', 'ignore')
                    i += 1
                if len(search_results) == 0:
                    print 'No results found, searching online..'
                    online = True
                    repeat = True
                    continue

                if not online:
                    print COLORS.bold + '[O] ' + COLORS.default + 'Search online'
                print COLORS.bold + '[C] ' + COLORS.default + 'Cancel'
                accepted = False
                while accepted == False:
                    which = raw_input(
                        COLORS.bold + 'Choose> ' + COLORS.default).replace('\n', '')
                    if which.lower() == 'o':
                        online = True
                        repeat = True
                        accepted = True
                    elif which.lower() == 'c':
                    	print ''
                    	accepted = True
                    elif which.isdigit():
                        if int(which) <= len(search_results):
                            search_picked = search_results[int(which)]
                            if entry_type in ['anime', 'manga']:
                                deep = ANN.details(search_picked['id'], entry_type)
                            elif entry_type == 'vn':
                                deep = VNDB.get(
                                    'vn', 'basic,details', '(id=' +\
                                     str(search_picked['id']) + ')', '')['items'][0]
                            accepted = True

            if which.lower() == 'c': continue
            genre = ''
            if which == 'n':
                genre = raw_input(
                    COLORS.bold + '<Genre> ' + COLORS.default).replace('\n', '')
            elif entry_type != 'vn':
                genres = ''
                for genre in deep['genres']:
                    genres = genres + genre + '/'
                genre = genres[:-1]

            if which != 'n':
                title = deep['title']

            status = ''
            while (status in ['c', 'w', 'h', 'q', 'd']) == False:
                status = raw_input(COLORS.bold + '<Status> ' + COLORS.default +
                                   COLORS.header + '[C/W/H/Q/D] ' +\
                                   COLORS.default).lower()[0]

            if status != 'w' and entry_type != 'vn':
                last_ep = raw_input(
                    COLORS.bold + '<Last episode watched> ' +\
                    COLORS.default).replace('\n', '')
            else:
                if entry_type == "anime":
                    last_ep = str(deep['episodes'])
                elif entry_type == "manga":
                    last_ep = str(deep['episodes'])
                else:
                    last_ep = ''

            obs = raw_input(
                COLORS.bold + '<Observations> ' +\
                COLORS.default).replace('\n', '')

            try:
                dbs[currentdb].dictionary['count'] += 1
            except AttributeError:
                dbs[currentdb].dictionary['count'] = 1
            dbs[currentdb].dictionary['items'].append({'id': dbs[currentdb
             ].dictionary['count'], 'type': entry_type,
             'aid': search_picked['id'],
             'name': utils.HTMLEntitiesToUnicode(
              utils.remove_html_tags(title)), 'genre':
	          utils.HTMLEntitiesToUnicode(utils.remove_html_tags(genre)),
              'status': status, 'lastwatched': last_ep, 'obs': obs})
            rebuild_ids(dbs[currentdb])
            print COLORS.green + 'Entry added' + COLORS.default + '\n'
        elif cmdsplit[0] == '':
            continue
        else:
            print COLORS.warning + 'Command not recognized' + COLORS.default
            continue


def print_help():
    """Prints this interface's help """
    ret = COLORS.header + 'Help for text interface' + COLORS.default + '\n'
    ret += COLORS.header + 'Usage: ' + COLORS.default + \
        sys.argv[0] + ' [filename] [options]\n\n'
    ret += '\t--create or -c initiates the database creation routine'
    return ret

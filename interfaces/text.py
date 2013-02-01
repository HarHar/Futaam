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
from interfaces.common import *
import os
import sys
import ConfigParser
import datetime

PS1 = '[%N]> '
configfile = os.path.join(os.getenv('USERPROFILE') or os.getenv('HOME'), '.futaam')
confs = ConfigParser.RawConfigParser()
if os.path.exists(configfile): confs.read(configfile)
try:
	PS1 = confs.get('Futaam', 'PS1')
except:
	PS1 = '[%green%%N%default%]> '
if PS1 == None: PS1 = '[%green%%N%default%]> '
if PS1[-1:] != ' ': PS1 += ' '

MAL = utils.MALWrapper()
colors = utils.colors()

def pickEntry(index, db):
	if index.isdigit() == False:
		print colors.fail + 'Argument must be the index number' + colors.default
		return None
	if db.dictionary['count'] < int(index) or int(index)<0:
		print colors.fail + 'Entry not found' + colors.default
		return None
	for entry in db.dictionary['items']:
		if entry['id'] == int(index): return entry
	else:
		print colors.fail + 'Entry not found! There is probably an error with your database and that makes me very sad :c' + colors.default
		return None

def main(argv):
	global PS1
	global configfile
	global confs
	global colors
	#GLOBAL VARIABLES ARRRRRGH

	dbfile = []
	host = ''
	port = 8500
	i = 0
	ircn = False
	for x in argv:
		if os.path.exists(x):
			dbfile.append(x)
		elif x == '--ircnotify':
			ircn = True
		elif x == '-c' or x == '--create':
			print colors.header + 'Creating database' + colors.default + '\n'
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
				print colors.fail + 'File exists' + colors.default
				sys.exit(1)
			dbtype = raw_input('Type [json/pickle] [json]> ').lower()
			if dbtype == '': dbtype = 'json'
			title = raw_input('Database name> ')
			if title == '': title = 'Unnamed'
			description = raw_input('Description of your database> ') #No need to have a default one
			parser.createDB(filename, dbtype, title, description)
			print '\n\n' + colors.green + 'Database created' + colors.default
			sys.exit(0)						
		elif x == '--host':
			if len(argv) <= i:
				print colors.fail + 'Missing host' + colors.default
				sys.exit(1)
			elif argv[i+1].startswith('--'):
				print colors.fail + 'Missing host' + colors.default
				sys.exit(1)	
			else:
				host = argv[i+1]
		elif x == '--port':
			if len(argv) <= i:
				print colors.fail + 'Missing port' + colors.default
				sys.exit(1)
			elif argv[i+1].startswith('--') or argv[i+1].isdigit() == False:
				print colors.fail + 'Missing port' + colors.default
				sys.exit(1)	
			else:
				port = int(argv[i+1])
		elif x == '--password':
			if len(argv) <= i:
				print colors.fail + 'Missing password' + colors.default
				sys.exit(1)
			elif argv[i+1].startswith('--'):
				print colors.fail + 'Missing password' + colors.default
				sys.exit(1)	
			else:
				password = argv[i+1]
		i += 1	
	if len(dbfile) == 0 and host == '':
		print colors.fail + 'No database specified' + colors.default
		print 'To create a database, use the argument "--create" or "-c" (no quotes)'
		sys.exit(1)

	if host == '':
		dbs = []
		for fn in dbfile:
			dbs.append(parser.Parser(fn, ircHook=ircn))
		currentdb = 0
	else:
		if password == '':
			print colors.fail + 'Missing password! ' + colors.default + 'Use "--password [pass]"'
			sys.exit(1)
		dbs = []
		dbs.append(parser.Parser(host=host, port=port, password=password))
		currentdb = 0

	print colors.header + dbs[currentdb].dictionary['name'] + colors.default + ' (' + dbs[currentdb].dictionary['description'] + ')'
	print 'Type help for cheat sheet'
	if len(dbs) > 1:
		print 'Type switchdb to change to the next database'
	sys.stdout.write('\n')

	while True:
		try:
			now = datetime.datetime.now()
			ps1_replace = {'%N': dbs[currentdb].dictionary['name'], '%D': dbs[currentdb].dictionary['description'], '%h': now.strftime('%H'), '%m': now.strftime('%M'), chr(37) + 's': now.strftime('%S'), '%blue%': colors.blue, '%green%': colors.green, '%red%': colors.fail, '%orange%': colors.warning, '%purple%': colors.header, '%default%': colors.default}
			ps1_temp = PS1
			ps1_temp = ps1_temp.replace('\%', '%' + chr(5))
			for x in ps1_replace:
				ps1_temp = ps1_temp.replace(x, ps1_replace[x])
			ps1_temp = ps1_temp.replace(chr(5), '')
			cmd = raw_input(ps1_temp + colors.default)
			cmdsplit = cmd.split(' ')
			args = ''
			for x in cmdsplit[1:]:
				args += x + ' '
			args = args[:-1]
		except (EOFError, KeyboardInterrupt):
			print colors.green + 'Bye~' + colors.default
			sys.exit(0)

		if cmdsplit[0].lower() in ['q', 'quit']:
			print colors.green + 'Bye~' + colors.default
			sys.exit(0)
		elif cmdsplit[0].lower() in ['set_ps1', 'sps1']:
			args += ' '
			if confs.sections().__contains__('Futaam') == False:
				confs.add_section('Futaam')
			confs.set('Futaam', 'PS1', args)
			with open(configfile, 'wb') as f:
				confs.write(f)
				f.close()
			PS1 = args
		elif cmdsplit[0].lower() in ['help', 'h']:
			print colors.header + 'Commands' + colors.default
			print '\thelp or h \t\t - prints this'
			print '\tquit or q \t\t - quits'
			print '\tset_ps1 or sps1 \t - changes PS1'
			print '\tswitchdb or sdb \t - changes working database when opened with multiple files'
			print '\tadd or a \t\t - adds an entry'
			print '\tdelete, del or d \t - deletes an entry with the given index'
			print '\tedit or e \t\t - edits an entry'
			print ''
		elif cmdsplit[0].lower() in ['switchdb', 'sdb']:
			try:
				currentdb += 1
				repr(dbs[currentdb])
			except IndexError:
				currentdb = 0
			print 'Current database: ' + colors.header + dbs[currentdb].dictionary['name'] + colors.default + ' (' + dbs[currentdb].dictionary['description'] + ')'
		elif cmdsplit[0].lower() in ['l', 'ls', 'list']:
			if len(dbs[currentdb].dictionary['items']) == 0:
				print colors.warning + 'No entries found! Use "add" for adding one' + colors.default
				continue
			else:
				for entry in dbs[currentdb].dictionary['items']:
					rcolors = {'d': colors.fail, 'c': colors.blue, 'w': colors.green, 'h': colors.warning, 'q': colors.header}
					if entry['status'].lower() in rcolors:
						sys.stdout.write(rcolors[entry['status'].lower()])
					print '\t' + str(entry['id']) + ' - [' + entry['status'].upper() + '] ' + entry['name'] + colors.default
		elif cmdsplit[0].lower() in ['d', 'del', 'delete']:
			entry = pickEntry(args, dbs[currentdb])
			if entry == None: continue
			confirm = ''
			while (confirm in ['y', 'n']) == False:
				confirm = raw_input(colors.warning + 'Are you sure? [y/n] ').lower()
			dbs[currentdb].dictionary['items'].remove(entry)
			dbs[currentdb].dictionary['count'] -= 1

			##### REBUILD IDS #####
			for x in xrange(0, dbs[currentdb].dictionary['count']):
				dbs[currentdb].dictionary['items'][x]['id'] = x
			#######################
			dbs[currentdb].save()
		elif cmdsplit[0].lower() in ['info', 'i']:
			entry = pickEntry(args, dbs[currentdb])
			if entry == None: continue

			if entry['type'] == 'anime':
				t_label = 'Last watched'
			else:
				t_label = 'Last chapter/volume read'
			toprint = {'Name': entry['name'], 'Genre': entry['genre'],
			 'Observations': entry['obs'], t_label: entry['lastwatched'],
			 'Status': utils.translated_status[entry['type']][entry['status'].lower()]}

			for k in toprint:
				print colors.bold + '<' + k + '>' + colors.default + ' ' + toprint[k]

		elif cmdsplit[0].lower() in ['edit', 'e']:
			#INTRO I
			entry = pickEntry(args, dbs[currentdb])
			if entry == None: continue

			#INTRO II
			n_name = raw_input('<Name> [' + entry['name'].encode('utf8') + '] ').replace('\n', '')
			n_genre = raw_input('<Genre> [' + entry['genre'].decode('utf8') + '] ').replace('\n', '')

			#ZIGZAGGING
			if entry['type'] == 'anime':
				n_status = """
					There was a time,
					when I was so brooken hearted;
					love wasn't much
					of a friend of miine..
				"""
				while (n_status in ['w', 'c', 'q', 'h', 'd', '']) == False:
					n_status = raw_input('<Status> [W/C/Q/H/D] [' + entry['status'].upper() + '] ').replace('\n', '').lower()
				n_lw = raw_input('<Last episode watched> [' + entry['lastwatched'] + ']> ').replace('\n', '')
			elif entry['type'] == 'manga':
				n_status = """
					BUT TABLES HAVE TURNED #yeah
					'cause me and them ways have parted;
					that kind of love
					WAS THE KILLING KIIND
				"""
				while (n_status in ['r', 'c', 'q', 'h', 'd', '']) == False:
					n_status = raw_input('<Status> [R/C/Q/H/D] [' + entry['status'].upper() + '] ').replace('\n', '').lower()
				if n_status == 'r': n_status = 'w'
				n_lw = raw_input('<Last page/chapter read> [' + entry['lastwatched'] + ']> ').replace('\n', '')

			#EXTENDED SINGLE NOTE
			n_obs = raw_input('<Observations> [' + entry['obs'] + ']> ')

			#BEGIN THE SOLO
			if n_name == '': n_name = entry['name']
			dbs[currentdb].dictionary['items'][int(args)]['name'] = utils.HTMLEntitiesToUnicode(utils.remove_html_tags(n_name))
			if n_genre == '': n_genre = entry['genre']
			dbs[currentdb].dictionary['items'][int(args)]['genre'] = utils.HTMLEntitiesToUnicode(utils.remove_html_tags(n_genre))
			if n_status == '': n_status = entry['status']
			dbs[currentdb].dictionary['items'][int(args)]['status'] = n_status
			if n_lw == '': n_lw = entry['lastwatched']
			dbs[currentdb].dictionary['items'][int(args)]['lastwatched'] = n_lw
			if n_obs == '': n_obs = entry['obs']
			dbs[currentdb].dictionary['items'][int(args)]['obs'] = n_obs

			#Peaceful end
			dbs[currentdb].save()
			print colors.green + 'Done' + colors.default
			continue
		elif cmdsplit[0].lower() in ['add', 'a']:
			title = ''
			while title == '': title = raw_input(colors.bold + '<Title> ' + colors.default).replace('\n', '')
			am = ''
			while (am in ['anime', 'manga']) == False: am = raw_input(colors.bold + '<Anime or Manga> ' + colors.default).lower()

			searchResults = MAL.search(title, am)
			i = 0
			for r in searchResults:
				print colors.bold + '[' + str(i) + '] ' + colors.default + r['title']
				i += 1
			print colors.bold + '[N] ' + colors.default + 'None of the above'
			accepted = False
			while accepted == False:
				which = raw_input(colors.bold + 'Choose> ' + colors.default).replace('\n', '')
				if which.lower() == 'n':
					accepted = True
				if which.isdigit():
					if int(which) <= len(searchResults):
						malanime = searchResults[int(which)]
						deep = MAL.details(malanime['id'], 'anime')
						accepted = True

			if which == 'n':
				genre = raw_input(colors.bold + '<Genre> ' + colors.default).replace('\n', '')
			else:
				g = ''
				for genre in deep['genres']:
					g = g + genre + '/'
				genre = g[:-1]
				title = deep['title']

			status = ''
			while (status in ['c', 'w', 'h', 'q', 'd']) == False: status = raw_input(colors.bold + '<Status> ' + colors.default + colors.header + '[C/W/H/Q/D] ' + colors.default).lower()[0]

			if status != 'w':
				lastEp = raw_input(colors.bold + '<Last episode watched> ' + colors.default).replace('\n', '')
			else:
				if am == "anime":
					lastEp = str(malanime['episodes'])
				else:
					lastEp = str(malanime['chapters'])

			obs = raw_input(colors.bold + '<Observations> ' + colors.default).replace('\n', '')

			try:
				dbs[currentdb].dictionary['count'] += 1
			except:
				dbs[currentdb].dictionary['count'] = 1
			dbs[currentdb].dictionary['items'].append({'id': dbs[currentdb].dictionary['count'], 'type': am, 'aid': malanime['id'], 'name': utils.HTMLEntitiesToUnicode(utils.remove_html_tags(title)), 'genre': utils.HTMLEntitiesToUnicode(utils.remove_html_tags(genre)), 'status': status, 'lastwatched': lastEp, 'obs': obs})
			for x in xrange(0, dbs[currentdb].dictionary['count']):
				dbs[currentdb].dictionary['items'][x]['id'] = x			
			dbs[currentdb].save()
			print colors.green + 'Entry added' + colors.default + '\n'
		else:
			print colors.warning + 'Command not recognized' + colors.default
			continue

def help():
	ret = colors.header + 'Help for text interface' + colors.default + '\n'
	ret += colors.header + 'Usage: ' + colors.default + sys.argv[0] + ' [filename] [options]\n\n'
	ret += '\t--create or -c initiates the database creation routine'
	return ret

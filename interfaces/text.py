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

from interfaces.common import *
import os
import sys
import ConfigParser
import datetime
import time

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

nyaa = utils.NyaaWrapper()
MAL = utils.MALWrapper()
vndb = utils.VNDB('Futaam', '0.1')
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
	hooks = []
	ircn = False
	for x in argv:
		if os.path.exists(x):
			dbfile.append(x)
		elif x == '--hook':
			if len(argv) <= i:
				print colors.fail + 'Missing hook name' + colors.default
				sys.exit(1)
			elif argv[i+1].startswith('--'):
				print colors.fail + 'Missing hook name' + colors.default
				sys.exit(1)
			else:
				if not (argv[i+1] in parser.availableHooks):
					print colors.fail + 'Hook not available' + colors.default
					sys.exit(1)
				else:
					hooks.append(parser.availableHooks[argv[i+1]]())
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
			dbs.append(parser.Parser(fn, hooks=hooks))
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
			args = args[:-1].replace('\n', '')
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
			print '\tdbtype or type \t\t - changes database type [json/pickle]'
			print '\tswitchdb or sdb \t - changes working database when opened with multiple files'
			print '\tadd or a \t\t - adds an entry'
			print '\tdelete, del or d \t - deletes an entry with the given index'
			print '\tedit or e \t\t - edits an entry'
			print '\tinfo or i\t\t - shows information on an entry'
			print '\toinfo or o\t\t - shows online information on an entry (if given entry number) or name'
			print '\tpicture, pic, image, img - shows an image of the entry or name'
			print '\tnyaa or n\t\t - searches nyaa.eu for torrent of an entry (if given entry number) or name'
			print '\tsort or s\t\t - swaps or moves entries around'
			print ''
		elif cmdsplit[0].lower() in ['setdbtype', 'dbtype', 'type']:
			if dbs[currentdb].host != '':
				print colors.fail + 'Changing database type is not supported on remote databases' + colors.default
				continue
			if len(cmdsplit) == 1:
				newtype = ''
				while (newtype in ['json', 'pickle']) == False: newtype = raw_input(colors.bold + '<New database type>' + colors.default + ' [json/pickle] ').replace('\n', '').lower()
			else:
				if (cmdsplit[1].lower() in ['json', 'pickle']) == False:
					print colors.warning + 'Invalid type. Use "json" or "pickle" as argument' + colors.default
					continue
				newtype = cmdsplit[1].lower()
			dbs[currentdb].dbtype = newtype
			dbs[currentdb].save()
			print colors.green + 'Done' + colors.default
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
				for entry in sorted(dbs[currentdb].dictionary['items'], key=lambda x: x['id']):
					rcolors = {'d': colors.fail, 'c': colors.blue, 'w': colors.green, 'h': colors.warning, 'q': colors.header}
						
					if entry['status'].lower() in rcolors:
						sys.stdout.write(rcolors[entry['status'].lower()])
					if os.name != 'nt':
						print '\t' + str(entry['id']) + ' - [' + entry['status'].upper() + '] ' + entry['name'] + colors.default
					else:
						print '\t' + str(entry['id']) + ' - [' + entry['status'].upper() + '] ' + entry['name'].encode('ascii', 'ignore') + colors.default

		elif cmdsplit[0].lower() in ['d', 'del', 'delete']:
			entry = pickEntry(args, dbs[currentdb])
			if entry == None: continue
			confirm = ''
			while (confirm in ['y', 'n']) == False:
				confirm = raw_input(colors.warning + 'Are you sure? [y/n] ' + colors.default).lower()
			dbs[currentdb].dictionary['items'].remove(entry)
			dbs[currentdb].dictionary['count'] -= 1

			##### REBUILD IDS #####
			for x in xrange(0, dbs[currentdb].dictionary['count']):
				dbs[currentdb].dictionary['items'][x]['id'] = x
			#######################
			dbs[currentdb].save()
		elif cmdsplit[0].lower() in ['image', 'img', 'picture', 'pic', 'pix']:
			accepted = False
			if args.isdigit():
				if args >= 0 and len(dbs[currentdb].dictionary['items']) >= int(args):
					eid = dbs[currentdb].dictionary['items'][int(args)]['aid']
					etype = dbs[currentdb].dictionary['items'][int(args)]['type']
					accepted = True
				else:
					print colors.fail + 'The entry '+ args +' is not on the list' + colors.default
			else:
				title = args

				am = ''
				while (am in ['anime', 'manga', 'vn']) == False: am = raw_input(colors.bold + '<Anime, Manga or VN> ' + colors.default).lower()

				if am in ['anime', 'manga']:
					searchResults = MAL.search(title, am)
				elif am == 'vn':
					searchResults = vndb.get('vn', 'basic', '(title~"' + title + '")', '')['items']
				if os.name == 'nt':
					for result in searchResults:
						for key in result:
							result[key] = result[key].encode('ascii', 'ignore')
				i = 0
				for r in searchResults:
					print colors.bold + '[' + str(i) + '] ' + colors.default + r['title']
					i += 1
				print colors.bold + '[A] ' + colors.default + 'Abort'
				while accepted == False:
					which = raw_input(colors.bold + 'Choose> ' + colors.default).replace('\n', '')
					if which.lower() == 'a':
						break
					if which.isdigit():
						if int(which) <= len(searchResults):
							malanime = searchResults[int(which)]

							eid = malanime['id']
							etype = am
							accepted = True

			if accepted:
				if etype in ['anime', 'manga']:
					deep = MAL.details(eid, etype)
				elif etype == 'vn':
					deep = vndb.get('vn', 'basic,details', '(id='+ str(eid) + ')', '')['items'][0]

				print colors.header + 'Fetching image, please stand by...' + colors.default
				utils.showImage(deep[('image_url' if etype != 'vn' else 'image')])
		elif cmdsplit[0].lower() in ['s', 'sort']:
			if len(cmdsplit) != 4:
				print 'Invalid number of arguments'
				print 'Must be:'
				print '	(s)ort [(s)wap/(m)ove] [index] [index]'
				print ''
				print 'When moving, first index should be "from entry" and second index should be "to entry"'
				continue

			if (cmdsplit[2].isdigit() == False) or (cmdsplit[3].isdigit() == False):
				print colors.fail + 'Indexes must be digits' + colors.default
				continue

			if cmdsplit[1].lower() in ['swap', 's']:
				#Swap ids
				dbs[currentdb].dictionary['items'][int(cmdsplit[2])]['id'] = int(cmdsplit[3])
				dbs[currentdb].dictionary['items'][int(cmdsplit[3])]['id'] = int(cmdsplit[2])

				#Re-sort
				dbs[currentdb].dictionary['items'] = sorted(dbs[currentdb].dictionary['items'], key=lambda x: x['id'])

				#Save
				dbs[currentdb].save()
			elif cmdsplit[1].lower() in ['move', 'm']:
				#Fool ids
				dbs[currentdb].dictionary['items'][int(cmdsplit[2])]['id'] = float(str(int(cmdsplit[3])-1) + '.5')

				#Re-sort
				dbs[currentdb].dictionary['items'] = sorted(dbs[currentdb].dictionary['items'], key=lambda x: x['id'])

				#Rebuild ids now that we have them in order
				for x in xrange(0, dbs[currentdb].dictionary['count']):
					dbs[currentdb].dictionary['items'][x]['id'] = x

				#Save
				dbs[currentdb].save()
			else:
				print colors.warning + 'Usage: (s)ort [(s)wap/(m)ove] [index] [index]' + colors.default
				continue
			
		elif cmdsplit[0].lower() in ['info', 'i']:
			entry = pickEntry(args, dbs[currentdb])
			if entry == None: continue

			if entry['type'].lower() in ['anime', 'manga']:
				if entry['type'].lower() == 'anime':
					t_label = 'Last watched'
				else:
					t_label = 'Last chapter/volume read'
				toprint = {'Name': entry['name'], 'Genre': entry['genre'],
				 'Observations': entry['obs'], t_label: entry['lastwatched'],
				 'Status': utils.translated_status[entry['type']][entry['status'].lower()]}
			elif entry['type'].lower() == 'vn':
				toprint = {'Name': entry['name'], 'Genre': entry['genre'],
				 'Observations': entry['obs'], 'Status': utils.translated_status[entry['type']][entry['status'].lower()]}

			for k in toprint:
				if os.name != 'nt':
					print colors.bold + '<' + k + '>' + colors.default + ' ' + unicode(toprint[k])
				else:
					print colors.bold + '<' + k + '>' + colors.default + ' ' + toprint[k].encode('ascii', 'ignore')

		elif cmdsplit[0].lower() in ['edit', 'e']:
			#INTRO I
			entry = pickEntry(args, dbs[currentdb])
			if entry == None: continue

			#INTRO II
			if os.name != 'nt':
				n_name = raw_input('<Name> [' + entry['name'].encode('utf8') + '] ').replace('\n', '')
			else:
				n_name = raw_input('<Name> [' + entry['name'].encode('ascii', 'ignore') + '] ').replace('\n', '')

			if entry['type'].lower() != 'vn':
				n_genre = raw_input('<Genre> [' + entry['genre'].decode('utf8') + '] ').replace('\n', '')


			#ZIGZAGGING
			n_lw = None
			n_status = None
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
			elif entry['type'] == 'vn':
				n_status = "This is a dummy text, there are many like it, but this one is mine.\n"
				while (n_status in ['p', 'c', 'q', 'h', 'd', '']) == False:
					n_status = raw_input('<Status> [P/C/Q/H/D] [' + entry['status'].upper() + '] ').replace('\n', '').lower()
				if n_status == 'p': n_status = 'w'
				n_lw = ''

			#EXTENDED SINGLE NOTE
			n_obs = raw_input('<Observations> [' + entry['obs'] + ']> ')

			#BEGIN THE SOLO
			if n_name == '': n_name = entry['name']
			dbs[currentdb].dictionary['items'][int(args)]['name'] = utils.HTMLEntitiesToUnicode(utils.remove_html_tags(n_name))
			if n_genre == '': n_genre = entry['genre']
			dbs[currentdb].dictionary['items'][int(args)]['genre'] = utils.HTMLEntitiesToUnicode(utils.remove_html_tags(n_genre))
			if n_status != None:
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
		elif cmdsplit[0].lower() in ['n', 'nyaa']:
			if args.isdigit():
				if args >= 0 and len(dbs[currentdb].dictionary['items']) >= int(args):
					term = dbs[currentdb].dictionary['items'][int(args)]['name']

					if dbs[currentdb].dictionary['items'][int(args)]['type'].lower() == 'anime':
						choice = ''
						while (choice in ['y', 'n']) == False:
							choice = raw_input(colors.bold + 'Do you want to choose a specific subbing group? [Y/n] ' + colors.default).lower()
							if choice.replace('\n', '') == '': choice = 'y'
						if choice == 'y':
							print colors.header + 'Please wait...' + colors.default
							groups = MAL.getGroupsList(dbs[currentdb].dictionary['items'][int(args)]['aid'], dbs[currentdb].dictionary['items'][int(args)]['name'])

							print ''
							i = 0
							for group in groups:
								if len(groups) > 1:
									print colors.bold + '[' + str(i) + '] ' + colors.default + str(group[0].replace('[', '').replace(']', '')) + ' - ' + str(group[1])
								else:
									print colors.bold + '[' + str(i) + '] ' + colors.default + str(group[0].replace('[', '').replace(']', ''))
								i += 1
							print '[C] Cancel'

							while True:
								which = raw_input(colors.bold + 'Choose> ' + colors.default).replace('\n', '')
								if which.lower() == 'c':
									break

								if which.isdigit():
									if int(which) <= len(groups):
										term = groups[int(which)][0] + ' ' + term
										break

						if dbs[currentdb].dictionary['items'][int(args)]['status'].lower() == 'c':
							if dbs[currentdb].dictionary['items'][int(args)]['lastwatched'].isdigit():
								choice = ''
								while (choice in ['y', 'n']) == False:
									choice = raw_input(colors.bold + 'Do you want to search for the next episode (' + str(int(dbs[currentdb].dictionary['items'][int(args)]['lastwatched']) + 1) + ')? [Y/n] ' + colors.default).lower()
									if choice.replace('\n', '') == '': choice = 'y'

								if choice == 'y':
									x = str(int(dbs[currentdb].dictionary['items'][int(args)]['lastwatched']) + 1)
									if len(str(x)) == 1:
										x = '0' + x
									#^^^ could go wrong
									term = term + ' ' + x

				else:
					print colors.fail + 'The entry '+ args +' is not on the list' + colors.default
					continue
			else:
				term = args

			print colors.header + 'Searching nyaa.eu for "' + term + '"...' + colors.default
			searchResults = nyaa.search(term)
			print ''

			if len(searchResults) == 0:
				print colors.fail + 'No results found' + colors.default
				continue

			i = 0
			for r in searchResults[:15]:
				if os.name != 'nt':
					print colors.bold + '[' + str(i) + '] ' + colors.default + r['title']
				else:
					print colors.bold + '[' + str(i) + '] ' + colors.default + r['title'].encode('ascii', 'ignore')
				i += 1
			print '[A] Abort'

			ok = False
			while ok == False: #Ugly I know
				which = raw_input(colors.bold + 'Choose> ' + colors.default).replace('\n', '')
				if which.lower() == 'a':
					break

				if which.isdigit():
					if int(which) <= len(searchResults) and int(which) <= 15:
						picked = searchResults[int(which)]
						ok = True

			if ok:
				print ''
				if os.name == 'nt':
					for key in picked:
						picked[key] == picked[key].encode('ascii', 'ignore')
				print colors.bold + '<Title> ' + colors.default + picked['title']
				print colors.bold + '<Category> ' + colors.default + picked['category']
				print colors.bold + '<Info> ' + colors.default + picked['description']
				print colors.bold + '<URL> ' + colors.default + picked['url']

				print ''
				choice = ''
				while (choice in ['t', 'd', 'n']) == False:
					print colors.bold + '[T] ' + colors.default + 'Download .torrent file'
					print colors.bold + '[D] ' + colors.default + 'Download all files (simple torrent client)'
					print colors.bold + '[N] ' + colors.default + 'Do nothing'
					choice = raw_input(colors.bold + 'Choose> ' + colors.default).lower()

				if choice == 't':
					metadata = urlopen(picked['url']).read()

					while True:
						filepath = raw_input(colors.bold + 'Save to> ' + colors.default).replace('\n', '')
						try:
							f = open(filepath, 'wb')
							f.write(metadata)
							f.close()
						except Exception, e:
							print colors.fail + 'Failed to save file' + colors.default
							print colors.fail + 'Exception! ' + str(e) + colors.default
							print 'Retrying...'
							print ''
							continue
						break

				if choice == 'd':
					try:
						import libtorrent as lt 
					except ImportError:
						print colors.fail + 'libTorrent Python bindings not found!' + colors.default
						print 'To install it check your distribution\'s package manager (python-libtorrent for Debian based ones) or compile libTorrent with the --enable-python-binding'
						continue

					print colors.header + 'Downloading to current folder...' + colors.default

					ses = lt.session()
					ses.listen_on(6881, 6891)
					e = lt.bdecode(urlopen(picked['url']).read())
					info = lt.torrent_info(e)
					h = ses.add_torrent(info, "./")

					while (not h.is_seed()):
							s = h.status()

							state_str = ['queued', 'checking', 'downloading metadata', \
									'downloading', 'finished', 'seeding', 'allocating', 'checking resume data']
							sys.stdout.write('\r\x1b[K%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % \
									(s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
									s.num_peers, state_str[s.state]))
							sys.stdout.flush()

							time.sleep(1)
					print ''

		elif cmdsplit[0].lower() in ['o', 'oinfo']:
			accepted = False
			if args.isdigit():
				if args >= 0 and len(dbs[currentdb].dictionary['items']) >= int(args):
					eid = dbs[currentdb].dictionary['items'][int(args)]['aid']
					etype = dbs[currentdb].dictionary['items'][int(args)]['type']
					accepted = True
				else:
					print colors.fail + 'The entry '+ args +' is not on the list' + colors.default
			else:
				title = args

				am = ''
				while (am in ['anime', 'manga', 'vn']) == False: am = raw_input(colors.bold + '<Anime, Manga or VN> ' + colors.default).lower()

				if am in ['anime', 'manga']:
					searchResults = MAL.search(title, am)
				elif am == 'vn':
					searchResults = vndb.get('vn', 'basic', '(title~"' + title + '")', '')['items']
				if os.name == 'nt':
					for result in searchResults:
						for key in result:
							result[key] = result[key].encode('ascii', 'ignore')
				i = 0
				for r in searchResults:
					print colors.bold + '[' + str(i) + '] ' + colors.default + r['title']
					i += 1
				print colors.bold + '[A] ' + colors.default + 'Abort'
				while accepted == False:
					which = raw_input(colors.bold + 'Choose> ' + colors.default).replace('\n', '')
					if which.lower() == 'a':
						break
					if which.isdigit():
						if int(which) <= len(searchResults):
							malanime = searchResults[int(which)]

							eid = malanime['id']
							etype = am
							accepted = True

			if accepted:
				if etype in ['anime', 'manga']:
					deep = MAL.details(eid, etype)
				elif etype == 'vn':
					deep = vndb.get('vn', 'basic,details', '(id='+ str(eid) + ')', '')['items'][0]

				if os.name == 'nt':
					for key in deep:
						deep[key] = deep[key].encode('ascii', 'ignore')

				if etype == 'anime':
					print colors.bold + 'Title: ' + colors.default + deep['title']
					if deep['end_date'] != None:
						print colors.bold + 'Year: ' + colors.default + deep['start_date'] + ' - ' + deep['end_date']
					else:
						print colors.bold + 'Year: ' + colors.default + deep['start_date'] + ' - ongoing'
					print colors.bold + 'Type: ' + colors.default + deep['type']
					print colors.bold + 'Classification: ' + colors.default + deep['classification']
					print colors.bold + 'Episodes: ' + colors.default + str(deep['episodes'])
					print colors.bold + 'Synopsis: ' + colors.default + utils.remove_html_tags(deep['synopsis'])
				elif etype == 'manga':
					print colors.bold + 'Title: ' + colors.default + deep['title']
					print colors.bold + 'Type: ' + colors.default + str(round(deep['members_score']))
					print colors.bold + 'Score: ' + colors.default + str(deep['chapters'])
					print colors.bold + 'Volumes: ' + colors.default + str(deep['volumes'])
					print colors.bold + 'Chapters: ' + colors.default + str(deep['chapters'])
					print colors.bold + 'Synopsis: ' + colors.default + utils.HTMLEntitiesToUnicode(utils.remove_html_tags(deep['synopsis']))
				elif etype == 'vn':
					if len(deep['aliases']) == 0:
						print colors.bold + 'Title: ' + colors.default + deep['title']
					else:
						print colors.bold + 'Title: ' + colors.default + deep['title'] + ' [' + deep['aliases'].replace('\n', '/') + ']'
						platforms = []
					for platform in deep['platforms']:
						names = {'lin': 'Linux', 'mac': 'Mac', 'win': 'Windows'}
						if platform in names:
							platform = names[platform]
						else: platform = platform[0].upper() + platform[1:]
						platforms.append(platform)
					print colors.bold + 'Platforms: ' + colors.default + ('/'.join(platforms))
					print colors.bold + 'Released: ' + colors.default + deep['released']
					print colors.bold + 'Languages: ' + colors.default + ('/'.join(deep['languages']))
					print colors.bold + 'Description: ' + colors.default + deep['description']

				print ''

		elif cmdsplit[0].lower() in ['add', 'a']:
			title = ''
			while title == '': title = raw_input(colors.bold + '<Title> ' + colors.default).replace('\n', '')
			am = ''
			while (am in ['anime', 'manga', 'vn']) == False: am = raw_input(colors.bold + '<Anime, Manga or VN> ' + colors.default).lower()

			if am in ['anime', 'manga']:
				searchResults = MAL.search(title, am)
			elif am == 'vn':
				searchResults = vndb.get('vn', 'basic', '(title~"' + title + '")', '')['items']
			i = 0
			for r in searchResults:
				if os.name != 'nt':
					print colors.bold + '[' + str(i) + '] ' + colors.default + r['title']
				else:
					print colors.bold + '[' + str(i) + '] ' + colors.default + r['title'].encode('ascii', 'ignore')
				i += 1
			print colors.bold + '[N] ' + colors.default + 'None of the above'
			accepted = False
			while accepted == False:
				which = raw_input(colors.bold + 'Choose> ' + colors.default).replace('\n', '')
				if which.lower() == 'n':
					accepted = True
				if which.isdigit():
					if int(which) <= len(searchResults):
						search_picked = searchResults[int(which)]
						if am in ['anime', 'manga']:
							deep = MAL.details(search_picked['id'], am)
						elif am == 'vn':
							deep = vndb.get('vn', 'basic,details', '(id='+ str(search_picked['id']) + ')', '')['items'][0]
						accepted = True

			genre = ''
			if which == 'n':
				genre = raw_input(colors.bold + '<Genre> ' + colors.default).replace('\n', '')
			elif am != 'vn':
				g = ''
				for genre in deep['genres']:
					g = g + genre + '/'
				genre = g[:-1]
				
			if which != 'n': title = deep['title']

			status = ''
			while (status in ['c', 'w', 'h', 'q', 'd']) == False: status = raw_input(colors.bold + '<Status> ' + colors.default + colors.header + '[C/W/H/Q/D] ' + colors.default).lower()[0]

			if status != 'w' and am != 'vn':
				lastEp = raw_input(colors.bold + '<Last episode watched> ' + colors.default).replace('\n', '')
			else:
				if am == "anime":
					lastEp = str(search_picked['episodes'])
				elif am == "manga":
					lastEp = str(search_picked['chapters'])
				else:
					lastEp = ''

			obs = raw_input(colors.bold + '<Observations> ' + colors.default).replace('\n', '')

			try:
				dbs[currentdb].dictionary['count'] += 1
			except:
				dbs[currentdb].dictionary['count'] = 1
			dbs[currentdb].dictionary['items'].append({'id': dbs[currentdb].dictionary['count'], 'type': am, 'aid': search_picked['id'], 'name': utils.HTMLEntitiesToUnicode(utils.remove_html_tags(title)), 'genre': utils.HTMLEntitiesToUnicode(utils.remove_html_tags(genre)), 'status': status, 'lastwatched': lastEp, 'obs': obs})
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

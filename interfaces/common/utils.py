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
import json
import urllib
import urllib2
import re
from HTMLParser import HTMLParser
from PIL import Image
import shutil
try:
	from BeautifulSoup import BeautifulStoneSoup
	from bs4 import BeautifulSoup
	from bs4 import UnicodeDammit
except:
	print 'You must have the python BeautifulSoup module: install pip and execute "pip install beautifulsoup; pip install beautifulsoup4", as root.'
	exit()

import os, inspect
from urllib2 import urlopen
from urllib import quote
from xml.dom import minidom
import socket
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from fuzzywuzzy import process

anime_translated_status = {'q': 'To watch', 'h': 'On hold', 'c': 'Currently watching', 'w': 'Watched', 'd': 'Dropped'}
manga_translated_status = {'q': 'To read', 'h': 'On hold', 'c': 'Currently reading', 'w': 'Read', 'd': 'Dropped'}
vn_translated_status = {'q': 'To play', 'c': 'Currently playing', 'h': 'On hold', 'd': 'Dropped', 'w': 'Played'}

translated_status = {'anime': anime_translated_status, 'manga': manga_translated_status, 'vn': vn_translated_status}

def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.iteritems():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d

def showImage(url):
    remote_fo = urllib2.urlopen(url)
    with open('tempfile.' + url.split('.')[len(url.split('.'))-1], 'wb') as local_fo:
        shutil.copyfileobj(remote_fo, local_fo)
    im = Image.open('tempfile.' + url.split('.')[len(url.split('.'))-1])
    im.show()

class colors():
    def __init__(self):
        self.enable()
    def enable(self):
    	if os.name == 'nt':
    		self.disable()
    		return
        self.header = '\033[95m'
        self.blue = '\033[94m'
        self.green = '\033[92m'
        self.warning = '\033[93m'
        self.fail = '\033[91m'
        self.bold = '\033[1m'
        self.default = '\033[0m'
    def disable(self):
        self.header = ''
        self.blue = ''
        self.green = ''
        self.warning = ''
        self.fail = ''
        self.default = ''
        self.bold = ''

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def HTMLEntitiesToUnicode(text):
    """Converts HTML entities to unicode.  For example '&amp;' becomes '&'."""
    text = unicode(BeautifulStoneSoup(text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
    return text

class NyaaWrapper(object):
	def search(self, term):
		results = []
		term = quote(term)

		rss = minidom.parse(urlopen("http://www.nyaa.eu/?page=rss&term="+term))
		items = rss.getElementsByTagName('item')

		for item in items:
			title = self.get_tag_value(item.getElementsByTagName('title')[0])
			url = self.get_tag_value(item.getElementsByTagName('link')[0])
			url = url.replace("&amp;", "&")
			description = self.get_tag_value(item.getElementsByTagName('description')[0])
			description = description.replace('<![CDATA[', '')
			description = description.replace(']]>', '')
			category = self.get_tag_value(item.getElementsByTagName('category')[0])
			results.append({'title': title, 'url': url, 'description': description, 'category': category})
		return results

	def get_tag_value(self, node):
		xml_str = node.toxml()
		start = xml_str.find('>')
		if start == -1:
			return ''
		end = xml_str.rfind('<')
		if end < start:
			return ''
		return xml_str[start + 1:end]	

class ANNWrapper(object):
	def __init__(self):
		self.searchURL = {'anime': 'http://cdn.animenewsnetwork.com/encyclopedia/api.xml?anime=~',
		'manga': 'http://cdn.animenewsnetwork.com/encyclopedia/api.xml?manga=~'}

		self.detailsURL = {'anime': 'http://cdn.animenewsnetwork.com/encyclopedia/api.xml?anime=',
		'manga': 'http://cdn.animenewsnetwork.com/encyclopedia/api.xml?manga='}

		self.reportURL = {'anime': 'http://cdn.animenewsnetwork.com/encyclopedia/reports.xml?id=155&type=anime&nlist=',
		'manga': 'http://cdn.animenewsnetwork.com/encyclopedia/reports.xml?id=155&type=manga&nlist='}

		self.URLEnc = lambda x: urllib.quote(x)

	def init(self):
		#Creates ~/.cache/futaam/ and populates it with the files ANN_anime_cache
		# and ANN_manga_cache
		self.caches = {}
		self.cacheDir = os.getenv('XDG_CACHE_HOME')
		if self.cacheDir is None: self.cacheDir = os.path.join(os.path.expanduser('~'), '.cache/futaam')
		if not os.path.exists(self.cacheDir):
			os.makedirs(self.cacheDir)
			for filename in ['ANN_anime_cache', 'ANN_manga_cache', 'ANN_id_cache', 'info']:
				open(os.path.join(self.cacheDir, filename), 'w').write('{}')
			for cache in ['ANN_anime_cache', 'ANN_manga_cache', 'ANN_id_cache', 'info']:
				self.caches[cache] = json.load(open(os.path.join(self.cacheDir, cache), 'r'))
			return 2 #2 for first time using ANNWrapper (needs to get populated)

		if len(self.caches) == 0:
			for cache in ['ANN_anime_cache', 'ANN_manga_cache', 'ANN_id_cache', 'info']:
				self.caches[cache] = json.load(open(os.path.join(self.cacheDir, cache), 'r'))

		if self.caches['info'].get('lastTimeUpdated', 0) > time.time() + 86400:
			return 1 #1 for need of daily update

		return 0 #0 for everything alright 

	def saveCache(self):
		for cache in self.caches:
			json.dump(self.caches[cache], open(os.path.join(self.cacheDir, cache), 'w'))

	def fetchReport(self, count):
		count = str(count)

		for stype in self.reportURL:
			if self.caches['ANN_id_cache'].get(stype) is None:
				self.caches['ANN_id_cache'][stype] = {}

			queryurl = self.reportURL[stype] + count
			res = urllib2.urlopen(queryurl).read()
			root = ET.fromstring(res)
			del res; res = etree_to_dict(root) #recycling is important

			#Merge fetched content to our id cache
			for item in res['report']['item']:
				self.caches['ANN_id_cache'][stype][item['name']] = item['id']

			#Update time of last update #lel
			self.caches['info']['lastTimeUpdated'] = time.time()
		self.saveCache()

	def mergeEntry(self, stype, entry):
		oldheight = 0

		self.caches['ANN_' + stype + '_cache'][entry['@id']] = {}
		self.caches['ANN_' + stype + '_cache'][entry['@id']]['id'] = entry['@id']
		self.caches['ANN_' + stype + '_cache'][entry['@id']]['title'] = entry['@name']
		self.caches['ANN_' + stype + '_cache'][entry['@id']]['type'] = entry['@type']
		self.caches['ANN_' + stype + '_cache'][entry['@id']]['other_titles'] = {'english': [], 'japanese': [], 'synonyms': []}
		self.caches['ANN_' + stype + '_cache'][entry['@id']]['image_url'] = ''
		self.caches['ANN_' + stype + '_cache'][entry['@id']]['genres'] = []
		self.caches['ANN_' + stype + '_cache'][entry['@id']]['OPsongs'] = []
		self.caches['ANN_' + stype + '_cache'][entry['@id']]['EDsongs'] = []
		self.caches['ANN_' + stype + '_cache'][entry['@id']]['episodes'] = None
		self.caches['ANN_' + stype + '_cache'][entry['@id']]['episode_names'] = {}
		for info in entry['info']:
			if info['@type'] == 'Alternative title':
				try: #yeeeeeeeaaaah...
					self.caches['ANN_' + stype + '_cache'][entry['@id']]['other_titles'][{'JA': 'japanese', 'EN': 'english'}[info['@lang']]] = info['#text']
				except: pass
			elif info['@type'] == 'Picture':
				self.caches['ANN_' + stype + '_cache'][entry['@id']]['image_url'] = info['@src']

				for img in info['img']:
					if int(img['@height']) > oldheight:
						self.caches['ANN_' + stype + '_cache'][entry['@id']]['image_url'] = img['@src']
						oldheight = int(img['@height'])
			elif info['@type'] in ['Genres', 'Themes']:
				self.caches['ANN_' + stype + '_cache'][entry['@id']]['genres'].append(info['#text'])
			elif info['@type'] == 'Plot Summary':
				self.caches['ANN_' + stype + '_cache'][entry['@id']]['synopsis'] = info['#text']
			elif info['@type'] == 'Opening Theme':
				self.caches['ANN_' + stype + '_cache'][entry['@id']]['OPsongs'].append(info['#text'])
			elif info['@type'] == 'Ending Theme':
				self.caches['ANN_' + stype + '_cache'][entry['@id']]['EDsongs'].append(info['#text'])
			elif info['@type'] == 'Number of episodes':
				self.caches['ANN_' + stype + '_cache'][entry['@id']]['episodes'] = int(info['#text'])
			elif info['@type'] == 'Vintage':
				if info['#text'].find(' to ') != -1:
					self.caches['ANN_' + stype + '_cache'][entry['@id']]['start_date'] = info['#text'].split(' to ')[0]
					self.caches['ANN_' + stype + '_cache'][entry['@id']]['end_date'] = info['#text'].split(' to ')[1]
				else:
					self.caches['ANN_' + stype + '_cache'][entry['@id']]['start_date'] = info['#text']
					self.caches['ANN_' + stype + '_cache'][entry['@id']]['end_date'] = None
			elif info['@type'] == 'Objectionable content':
				self.caches['ANN_' + stype + '_cache'][entry['@id']]['classification'] = info['#text']
		if len(entry.get('episode', [])) > 0:
			for episode in entry['episode']:
				self.caches['ANN_' + stype + '_cache'][entry['@id']]['episode_names'][episode['@num']] = episode['title']['#text']

	def search(self, name, stype, online=False):
		if online:
			queryurl = self.searchURL[stype] + self.URLEnc(name)
			res = urllib2.urlopen(queryurl).read()
			root = ET.fromstring(res)
			del res; res = etree_to_dict(root)
			if res['ann'].get(stype) is None:
				return []
			
			foundlings = []
			rawfoundlings = []

			if "@id" in res['ann'][stype]:
				entry = res['ann'][stype]
				foundlings.append({'id': entry['@id'], 'title': entry['@name']})
				self.mergeEntry(stype, entry)
			else:
				for entry in res['ann'][stype]:
					if name.lower() in entry['@name'].lower():
						foundlings.append({'id': entry['@id'], 'title': entry['@name']})
						rawfoundlings.append(entry['@name'])
						self.mergeEntry(stype, entry)
			self.saveCache()
		else:
			foundlings = []
			rawfoundlings = []
			
			for item in self.caches['ANN_id_cache'][stype]:
				if name.lower() in item.lower():
					foundlings.append({'id': self.caches['ANN_id_cache'][stype][item], 'title': item})
					rawfoundlings.append(item)

		for found in process.extract(name, self.caches['ANN_id_cache'][stype], limit=10):
			if found[1] >= 69:
				if found[0] in rawfoundlings:
					continue
				foundlings.append({'title': found[0], 'id': self.caches['ANN_id_cache'][stype][found[0]]})

		return foundlings

	def details(self, eid, stype):
		if str(eid) in self.caches['ANN_' + stype + '_cache'].keys():
			return self.caches['ANN_' + stype + '_cache'][str(eid)]

		queryurl = self.detailsURL[stype] + str(eid)
		res = urllib2.urlopen(queryurl).read()
		root = ET.fromstring(res)
		del res; res = etree_to_dict(root)
		
		self.mergeEntry(stype, res['ann'][stype])
		self.saveCache()
			
		if str(eid) in self.caches['ANN_' + stype + '_cache'].keys():
			return self.caches['ANN_' + stype + '_cache'][str(eid)]
		raise Exception('Entry with specified ID not found')

class MALWrapper(object):
	@staticmethod
	def search(name, stype):
		if not stype in ['anime', 'manga']:
			raise TypeError('second parameter must be either "anime" or "manga"') #I know, TypeError isn't meant for that, but meh

		try:
			n = unicodedata.normalize('NFKD', name).encode('ascii','ignore')
		except:
			n = name
		params = urllib.urlencode({'q': n})
		queryurl = 'http://mal-api.com/'+ stype + '/search?%s' % params
		res = urllib2.urlopen(queryurl)
		dict = json.load(res)
		return dict
	@staticmethod
	def details(id, stype):
		if not stype in ['anime', 'manga']:
			raise TypeError('second parameter must be either "anime" or "manga"')
		queryurl = 'http://mal-api.com/'+ stype +'/'+str(id)
		res = urllib2.urlopen(queryurl)
		dict = json.load(res)
		return dict
	@staticmethod
	def getGroupsList(animeId, animeTitle):
		"""Returns a list of tuples in the following form
				[('GroupName', 'details'), ('GroupName', 'details'), ('GroupName', None)]
		"""
		url = 'http://myanimelist.net/anime/' + str(animeId) + '/' + urllib.quote(animeTitle) ##Anime only?
		c = urllib2.urlopen(url).read()
		bs = BeautifulSoup(c)

		smalls = []
		for div in bs.findAll('div'):
			if div.get('class') == ['spaceit_pad']:
				smalls.append(div.findAll('small'))

		x = []
		for tags in smalls:
			if len(tags) != 0:
				if tags[0].getText().startswith('[') == False or tags[0].getText().endswith(']') == False: continue

			if len(tags) > 1:
				x.append((tags[0].getText(), tags[1].getText()))
			elif len(tags) == 1:
				x.append((tags[0].getText(), None))

		return x
	@staticmethod
	def getCharacterList(animeId, animeTitle, stype):
		if not stype in ['anime', 'manga']:
			raise TypeError('second parameter must be either "anime" or "manga"')

		url = 'http://myanimelist.net/'+ stype +'/' + str(animeId) + '/' + urllib.quote(animeTitle) + '/characters'
		c = urllib2.urlopen(url).read().replace("'+'", '').replace("' + '", '')
		bs = BeautifulSoup(c)

		i = 0
		girls = []
		for t in bs.findAll('td')[11:]:
		        try:
		                spl = t.getText().split('\n')
		                if spl[1] in girls:
		                	continue
		                if spl[2].find('Main') != -1 or spl[2].find('Supporting') != -1:
		                        girls.append(spl[1])
		        except:
		                pass
		        i += 1

		d = []
		for b in girls:
			if b.find(',') != -1:
				s = b.split(',')
				b = s[1] + ' ' + s[0]
			d.append(b.lstrip().rstrip().strip('\n'))	        

		ids = []
		for l in bs.findAll('a'):
			try:
				if l.get('href').find('character') == -1: continue
			except:
				continue
			for g in girls:
				try:
					if l.get('href').split('/')[4] in ids:
						continue
					if l.getText() == g:
						ids.append(l.get('href').split('/')[4])
				except:
					continue

		thumbnails = []
		for img in bs.findAll('div'):
			if img.get('class') != ['picSurround']: continue
			try:
				if img.find('a').get('href').find('character') == -1:
					continue		
					print repr(img.find('a').get('href')) + ' - ' + repr(img.find('a').find('img').get('src'))
			except:
				continue

			for g in girls:
				try:
					if img.find('a').find('img').get('src').find('questionmark') == -1 and img.find('a').find('img').get('src') in thumbnails:
						continue
					if img.find('a').get('href').find(g.split(' ')[0]) != -1:
						thumbnails.append(img.find('a').find('img').get('src'))
						continue

					if img.find('a').get('href').find(g.split(' ')[1]) != -1:
						thumbnails.append(img.find('a').find('img').get('src'))
				except:
					continue		

		return (d, ids, thumbnails)
	@staticmethod
	def getCharacterInfo(name, id, raw=False):
		c = urllib2.urlopen('http://myanimelist.net/character/' + str(id))
		d = c.read()

		dammit = UnicodeDammit(d.replace("'+'", '').replace("' + '", ''))

		summary = dammit.unicode_markup.split('<div class="normal_header" style="height: 15px;">' + name)[1]
		summary = summary.split('</div>')[1]
		summary = summary.split('<div')[0]

		jpname = name + dammit.unicode_markup.split('<div class="normal_header" style="height: 15px;">' + name)[1].split('</div>')[0]

		bs = BeautifulSoup(dammit.unicode_markup)

		img = ''
		for image in bs.findAll('img'):
			try:
				if image.get('alt').find(name) != -1:
					img = image.get('src')
					break
			except: continue

		if raw == False:
			return (HTMLEntitiesToUnicode(remove_html_tags(jpname)), HTMLEntitiesToUnicode(remove_html_tags(summary)).rstrip('\n').lstrip('\n'), img)
		else:
			return (jpname, summary, img, name)


class vndbException(Exception):
	pass

class VNDB(object):
	""" Python interface for vndb's api (vndb.org), featuring cache """
	protocol = 1
	def __init__(self, clientname, clientver, username=None, password=None, debug=False):
		if '--no-vndb' in __import__('sys').argv:
			return
		self.sock = socket.socket()
		
		if debug: print('Connecting to api.vndb.org')
		try:
			self.sock.connect(('api.vndb.org', 19534))
		except:
			print('Could not connect to VNDB')
			return
		if debug: print('Connected')
		
		if debug: print('Authenticating')
		if (username == None) or (password == None):
			self.sendCommand('login', {'protocol': self.protocol, 'client': clientname,
				'clientver': float(clientver)})
		else:
			self.sendCommand('login', {'protocol': self.protocol, 'client': clientname,
				'clientver': float(clientver), 'username': username, 'password': password})
		res = self.getRawResponse()
		if res.find('error ') == 0:
			raise vndbException(json.loads(' '.join(res.split(' ')[1:]))['msg'])
		if debug: print('Authenticated')
		
		self.cache = {'get': []}
		self.cachetime = 720 #cache stuff for 12 minutes
	def close(self):
		self.sock.close()	
	def get(self, type, flags, filters, options):
		""" Gets a VN/producer
		
		Example:
		>>> results = vndb.get('vn', 'basic', '(title="Clannad")', '')
		>>> results['items'][0]['image']
		u'http://s.vndb.org/cv/99/4599.jpg'
		"""
		args = '{0} {1} {2} {3}'.format(type, flags, filters, options)
		for item in self.cache['get']:
			if (item['query'] == args) and (time.time() < (item['time'] + self.cachetime)):
				return item['results']
				
		self.sendCommand('get', args)
		res = self.getResponse()[1]
		self.cache['get'].append({'time': time.time(), 'query': args, 'results': res})
		return res

	def sendCommand(self, command, args=None):
		""" Sends a command
		
		Example
		>>> self.sendCommand('test', {'this is an': 'argument'})
		"""
		whole = ''
		whole += command.lower()
		if isinstance(args, basestring):
			whole += ' ' + args
		elif isinstance(args, dict):
			whole += ' ' + json.dumps(args)
		
		self.sock.send('{0}\x04'.format(whole))
	
	def getResponse(self):
		""" Returns a tuple of the response to a command that was previously sent
		
		Example
		>>> self.sendCommand('test')
		>>> self.getResponse()
		('ok', {'test': 0})
		"""
		res = self.getRawResponse()
		cmdname = res.split(' ')[0]
		if len(res.split(' ')) > 1:
			args = json.loads(' '.join(res.split(' ')[1:]))
			
		if cmdname == 'error':
			if args['id'] == 'throttled':
				raise vndbException('Throttled, limit of 100 commands per 10 minutes')
			else:
				raise vndbException(args['msg'])
		return (cmdname, args)
	def getRawResponse(self):
		""" Returns a raw response to a command that was previously sent 
		
		Example:
		>>> self.sendCommand('test')
		>>> self.getRawResponse()
		'ok {"test": 0}'
		"""
		finished = False
		whole = ''
		while not finished:
			whole += self.sock.recv(4096)
			if '\x04' in whole: finished = True
		return whole.replace('\x04', '').strip()


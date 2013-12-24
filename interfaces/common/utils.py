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

def google(search):
    query = urllib.urlencode({'q': search})
    response = urllib.urlopen('http://ajax.googleapis.com/ajax/services/search/web?v=1.0&' + query).read()
    j = json.loads(response)
    results = j['responseData']['results']
    for result in results:
        #title = result['title']
        #print repr(result['title']) + ' -- ' + repr(result['url'])
        yield (result['title'], urllib.unquote(result['url']))

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
	"""Provides a wrapper to ANN's Encyclopedia's XML API. It will 
	automatically cache data localy to speed up searching."""

	def __init__(self):
		"""Sets up constant urls but not initialize the local ANN cache."""
		self.searchURL = {'anime': 'http://cdn.animenewsnetwork.com/encyclopedia/api.xml?anime=~',
		'manga': 'http://cdn.animenewsnetwork.com/encyclopedia/api.xml?manga=~'}

		self.detailsURL = {'anime': 'http://cdn.animenewsnetwork.com/encyclopedia/api.xml?anime=',
		'manga': 'http://cdn.animenewsnetwork.com/encyclopedia/api.xml?manga='}

		self.reportURL = {'anime': 'http://cdn.animenewsnetwork.com/encyclopedia/reports.xml?id=155&type=anime&nlist=',
		'manga': 'http://cdn.animenewsnetwork.com/encyclopedia/reports.xml?id=155&type=manga&nlist='}

		self.URLEnc = lambda x: urllib.quote(x)

	def init(self):
		"""Creates ~/.cache/futaam/ and populates it with the files ANN_anime_cache
		and ANN_manga_cache."""
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

		if self.caches['info'].get('lastTimeUpdated', 0) + 86400 < time.time():
			return 1 #1 for need of daily update

		return 0 #0 for everything alright 

	def save_cache(self):
		"""Saves the ANN cache to the disk."""
		for cache in self.caches:
			json.dump(self.caches[cache], open(os.path.join(self.cacheDir, cache), 'w'))

	def fetch_report(self, count):
		"""HarHar will need to explain this one ¯\(°_o)/¯"""
		count = str(count)

		for stype in self.reportURL:
			if self.caches['ANN_id_cache'].get(stype) is None:
				self.caches['ANN_id_cache'][stype] = {}

			queryurl = self.reportURL[stype] + count
			try:
				res = urllib2.urlopen(queryurl).read()
			except urllib2.URLError:
				return
			root = ET.fromstring(res)
			del res; res = etree_to_dict(root) #recycling is important

			#Merge fetched content to our id cache
			for item in res['report']['item']:
				self.caches['ANN_id_cache'][stype][item['name']] = item['id']

			#Update time of last update #lel
			self.caches['info']['lastTimeUpdated'] = time.time()
		self.save_cache()

	def merge_entry(self, stype, entry):
		"""Merges a new entry into the cache."""
		oldheight = 0
		to_be_merged = {}
		to_be_merged['id'] = entry['@id']
		to_be_merged['title']  = entry['@name']
		to_be_merged['type'] = entry['@type']
		to_be_merged['other_titles'] = {'english': [], 'japanese': [], 'synonyms': []}
		to_be_merged['image_url'] = ''
		to_be_merged['genres'] = []
		to_be_merged['OPsongs'] = []
		to_be_merged['EDsongs'] = []
		to_be_merged['episodes'] = None
		to_be_merged['episode_names'] = {}
		to_be_merged['characters'] = {}
		to_be_merged['staff'] = {}
		to_be_merged['credit'] = []

		for info in entry['info']:
			if info['@type'] == 'Alternative title':
				try: #yeeeeeeeaaaah...
					to_be_merged['other_titles'][{'JA': 'japanese', 'EN': 'english'}[info['@lang']]] = info['#text']
				except: 
					pass
			elif info['@type'] == 'Picture':
				to_be_merged['image_url'] = info['@src']

				for img in info['img']:
					if type(img) == str:
						continue
					if int(img['@height']) > oldheight:
						to_be_merged['image_url'] = img['@src']
						oldheight = int(img['@height'])
			elif info['@type'] in ['Genres', 'Themes']:
				to_be_merged['genres'].append(info['#text'])
			elif info['@type'] == 'Plot Summary':
				to_be_merged['synopsis'] = info['#text']
			elif info['@type'] == 'Opening Theme':
				to_be_merged['OPsongs'].append(info['#text'])
			elif info['@type'] == 'Ending Theme':
				to_be_merged['EDsongs'].append(info['#text'])
			elif info['@type'] == 'Number of episodes':
				to_be_merged['episodes'] = int(info['#text'])
			elif info['@type'] == 'Vintage':
				if info['#text'].find(' to ') != -1:
					to_be_merged['start_date'] = info['#text'].split(' to ')[0]
					to_be_merged['end_date'] = info['#text'].split(' to ')[1]
				else:
					to_be_merged['start_date'] = info['#text']
					to_be_merged['end_date'] = None
			elif info['@type'] == 'Objectionable content':
				to_be_merged['classification'] = info['#text']

		for episode in entry.get('episode', []):
			if to_be_merged['episode_names'].get(episode['@num']) != None:
				to_be_merged['episode_names'][episode['@num']] += ' / ' + episode['title']['#text'] + ' (' + episode['title']['@lang'] + ')'
			else:
				to_be_merged['episode_names'][episode['@num']] = episode['title']['#text'] + ' (' + episode['title']['@lang'] + ')'

		for cast in entry.get('cast', []):
			to_be_merged['characters'][cast['role']] = cast['person']['#text']

		for staff in entry.get('staff', []):
			to_be_merged['staff'][staff['person']['#text']] = staff['task']
		
		if type(entry.get('credit')) == dict:
			to_be_merged['credit'].append(entry['credit']['company']['#text'])
		else:
			for credit in entry.get('credit', []):
				to_be_merged['credit'].append(credit['company']['#text'])

		if len(entry.get('episode', [])) > 0:
			for episode in entry['episode']:
				to_be_merged['episode_names'][episode['@num']] = episode['title']['#text']

		self.caches['ANN_' + stype + '_cache'][entry['@id']] = to_be_merged

	def search(self, name, stype, online=False):
		"""Searches locally or online for the given name."""
		if online:
			foundlings = []
			for title, url in google(name + ' inurl:animenewsnetwork.com'):
				split = url.split('http://www.animenewsnetwork.com/encyclopedia/anime.php?id=')
				if len(split) > 1:
					foundlings.append({'id': int(split[1]), 'title': remove_html_tags(HTMLEntitiesToUnicode(title.replace(' - Anime News Network', '')))})
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
		"""Returns the details for the given ANN entry ID."""
		if str(eid) in self.caches['ANN_' + stype + '_cache'].keys():
			return self.caches['ANN_' + stype + '_cache'][str(eid)]

		queryurl = self.detailsURL[stype] + str(eid)
		res = urllib2.urlopen(queryurl).read()
		root = ET.fromstring(res)
		del res; res = etree_to_dict(root)
		
		self.merge_entry(stype, res['ann'][stype])
		self.save_cache()
			
		if str(eid) in self.caches['ANN_' + stype + '_cache'].keys():
			return self.caches['ANN_' + stype + '_cache'][str(eid)]
		raise Exception('Entry with specified ID not found')

class vndbException(Exception):
	pass

class VNDB(object):
	""" Python interface for vndb's api (vndb.org), featuring cache """
	protocol = 1
	def __init__(self, clientname, clientver, username=None, password=None, debug=False, forReal=False):
		if '--no-vndb' in __import__('sys').argv:
			return

		if not forReal:
			self.initialized = False
			self.initArgs = (clientname, clientver, username, password, debug, True)
			return
		self.initialized = True

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
		if not self.initialized: self.__init__(*self.initArgs) #<-- lol

		self.sock.close()
	def get(self, type, flags, filters, options):
		""" Gets a VN/producer
		
		Example:
		>>> results = vndb.get('vn', 'basic', '(title="Clannad")', '')
		>>> results['items'][0]['image']
		u'http://s.vndb.org/cv/99/4599.jpg'
		"""
		if not self.initialized: self.__init__(*self.initArgs)

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
		if not self.initialized: self.__init__(*self.initArgs)

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
		if not self.initialized: self.__init__(*self.initArgs)

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
		if not self.initialized: self.__init__(*self.initArgs)

		finished = False
		whole = ''
		while not finished:
			whole += self.sock.recv(4096)
			if '\x04' in whole: finished = True
		return whole.replace('\x04', '').strip()


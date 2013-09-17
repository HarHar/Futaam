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


anime_translated_status = {'q': 'To watch', 'h': 'On hold', 'c': 'Currently watching', 'w': 'Watched', 'd': 'Dropped'}
manga_translated_status = {'q': 'To read', 'h': 'On hold', 'c': 'Currently reading', 'w': 'Read', 'd': 'Dropped'}
vn_translated_status = {'q': 'To play', 'c': 'Currently playing', 'h': 'On hold', 'd': 'Dropped', 'w': 'Played'}

translated_status = {'anime': anime_translated_status, 'manga': manga_translated_status, 'vn': vn_translated_status}

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
		url = 'http://myanimelist.net/anime/' + str(animeId) + '/' + urllib.quote(animeTitle) + '/characters' ##Anime only?
		c = urllib2.urlopen(url).read().replace("'+'", '').replace("' + '", '')
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


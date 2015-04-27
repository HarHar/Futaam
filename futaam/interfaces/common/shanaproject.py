#!/usr/bin/env python
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import json
import os.path
import datetime

try:
	from BeautifulSoup import BeautifulStoneSoup
	from bs4 import BeautifulSoup
	from bs4 import UnicodeDammit
except:
	print('You must have the python BeautifulSoup module: install pip and execute "pip install beautifulsoup; pip install beautifulsoup4", as root.')
	exit()

cp = os.path.join(os.environ['HOME'], '.futaam')

class ShanaParser(object):
	def __init__(self, url="http://www.shanaproject.com/season/list/?sort=date", confpath=cp):
		self.url = url
		self.confpath = confpath
		self.reloadConf()
	def reloadConf(self):
		self.conf = json.load(open(self.confpath, 'r'))
	def saveConf(self):
		json.dump(self.conf, open(self.confpath, 'w'))
	def currentSeason(self):
		today = datetime.date.today()
		if not (self.conf.get('{0}/{1}'.format(today.month, today.year)) is None):
			return self.conf['{0}/{1}'.format(today.month, today.year)]

		soup = BeautifulSoup(urllib.request.urlopen(self.url).read())
		divs = []
		for el in soup.findAll('div'):
			if el.get('class') != None:
				if 'header_display_box' in el['class']:
					divs.append(el)
		shows = []
		for el in divs:
			shows.append(el.findAll('h3')[0].getText())

		self.conf['{0}/{1}'.format(today.month, today.year)] = shows
		self.saveConf()

		return shows
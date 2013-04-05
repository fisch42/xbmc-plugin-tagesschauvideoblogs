# -*- coding: utf-8 -*-

from xbmcswift2 import Plugin, xbmc, xbmcgui
import urllib2,urllib,re,feedparser,HTMLParser

plugin = Plugin()

tagesschauURL = 'http://www.tagesschau.de/'

h264regexp  = re.compile('http:\/\/[^"]+webl\.h264\.mp4')
videoregexp = re.compile(re.escape(tagesschauURL)+'videoblog\/[^"]+')

blogsregexp      = re.compile('leftNavL2(.*)sendungenLeft', re.MULTILINE|re.DOTALL)
blogurlregexp    = re.compile('a href="(\/videoblog\/[^"]+)"')
blogtitleregexp  = re.compile('i2">([^<]+)<')
entriesregexp    = re.compile('<h2><a[^>]href="\/([^"]+)[^>]+title="([^"]+)')

def removeNonAscii(s):
	return "".join(i for i in s if ord(i)<128)

def parseTitle(title):
	if title.startswith('Videoblog: '):
		return title[11:]
	elif title.startswith('Videoblog '):
		return title[10:]
	else:
		return title

def getVideoPageUrl(desc):
	match = videoregexp.search(desc)
	return match.group(0)

def getH264Video(url):
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	html = response.read()
	response.close()
	match = h264regexp.search(html)
	return match.group(0)

def getBlogs():
	req = urllib2.Request(tagesschauURL+'videoblog/index.html')
	response = urllib2.urlopen(req)
	html = response.read()
	response.close()
	match = blogsregexp.search(html)
	text = match.group(0)
	matchUrl = blogurlregexp.findall(text)
	matchTitle = blogtitleregexp.findall(text)
	h = HTMLParser.HTMLParser()
	objs = []
	i = 0
	for url in matchUrl:
		obj = {
			'title': h.unescape(removeNonAscii(matchTitle[i])),
			'url': tagesschauURL+url
		}
		objs.append(obj)
		i = i + 1
	return objs

def getEntries(url):
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	html = response.read()
	response.close()
	entries = entriesregexp.findall(html)
	h = HTMLParser.HTMLParser()
	objs = []
	for entry in entries:
		obj = {
			'title': entry[1],
			'url': tagesschauURL+entry[0]
		}
		objs.append(obj)
	return objs

@plugin.route('/')
def index():
	item = {
		'label': 'Neueste',
		'path': plugin.url_for('show_newest')
	}
	item2 = {
		'label': 'Alle',
		'path': plugin.url_for('show_all')
	}
	return [item, item2]

@plugin.route('/newest/')
def show_newest():
	feed = feedparser.parse('http://meta.tagesschau.de/tag/videoblog/feed')
	items = []
	for entry in feed.entries:
		item = {
			'label': parseTitle(entry.title),
			'path': getH264Video(getVideoPageUrl(entry.description)),
			'is_playable': True
		}
		items.append(item)
		
	return items

@plugin.route('/blogs/')
def show_all():
	items = []
	blogs = getBlogs()
	for blog in blogs:
		item = {
			'label': blog['title'],
			'path': plugin.url_for('show_blog', blog=urllib.quote(blog['url']))
		}
		items.append(item)
		
	return items

@plugin.route('/blogs/<blog>')
def show_blog(blog):
	items = []
	url = urllib.unquote(blog)
	entries = getEntries(url)
	for entry in entries:
		item = {
			'label': entry['title'],
			'path': getH264Video(entry['url']),
			'is_playable': True
		}
		items.append(item)	
	return items

if __name__ == '__main__':
	plugin.run()

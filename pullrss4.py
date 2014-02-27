from future import Future
import feedparser
import re
import MySQLdb as mdb
from datetime import datetime
import time
import HTMLParser


def unencode_text(text):
	try:
		cleantext = html_parser.unescape(text)
	except:
		print 'Error with escaping %s' % text
		cleantext = ''
	return cleantext

def decode_text(text):
	try:
		# remove odd characters, then decode
		normtext = text.replace(u'\u2019','\'').replace(u'\u2018','\'')
		normtext = normtext.replace(u'\xbd','').replace(u'\xa0','')
		normtext = normtext.replace(u'\u201c','\"').replace(u'\u201d','\"')
		normtext = normtext.replace(u'\xe9','e').replace(u'\xe0','a').replace(u'\xe8','e').replace(u'\xf8','o').replace(u'\xe1','a')
		normtext = normtext.replace(u'\u2014', '-').replace(u'\u2013', '-')
		normtext = normtext.replace(u'\u2026', '...')
		normtext = normtext.replace(u'\u2009', '')
		cleantext = normtext.decode('utf8','ignore')
	except:
		print 'Error with decoding %s' % text
		cleantext = ''
	return cleantext

def extract_pubdate(text):
	''' convert time.strftime to mysql date format '''
	dt = datetime.fromtimestamp(time.mktime(text))
	date = dt.strftime('%Y-%m-%d')
	return date


def extract_summarytext(entry):
	''' extract the text from an rss story '''
	summary = entry['summary']
	match = re.search(r'([^<]*)', summary)
	# first look in the summary
	if match:
		summarytext = match.group(1)
		#summarytext = summarytext.replace("&rsquo;", "'")
		#summarytext = summarytext.replace("\\", "")
		#summarytext = summarytext.encode("ascii", "ignore")
		#summarytext = html_parser.unescape(summarytext)
		summarytext = unencode_text(summarytext)

	# second look in the title
	else:
		title = entry['title']
		#title = title.encode("ascii", "ignore")
		#title = html_parser.unescape(title)
		title = unencode_text(title)
		match = re.search(r'(.+)', title)
		if match:
			summarytext = match.group(1)
		# otherwise return empty
		else:
			summarytext = ""

	return summarytext


with open('hitlist.txt', 'r') as f:
	hit_list = [hit for hit in f.read().split('\n') if hit] # list of feeds to pull down
 
# pull down all feeds
#future_calls = [Future(feedparser.parse,rss_url) for rss_url in hit_list]
# block until they are all in
#feeds = [future_obj() for future_obj in future_calls]
feeds = [feedparser.parse(rss_url) for rss_url in hit_list]


entries = []
for feed in feeds:
	entries.extend( feed[ "items" ] )

# use this to escape html characters
html_parser = HTMLParser.HTMLParser()
# extract info, put in MySQL db
# connect to the mySQL database rssfeeddata
con = mdb.connect('localhost', 'testuser', 'test123', 'rssfeeddata', charset='utf8')
with con:
	cur = con.cursor(mdb.cursors.DictCursor)
 	# in entries, I want link and summary and title and published.
 	# need to parse summary to text
	for entry in entries:
		title = entry["title"]
		#title = title.encode("ascii", "ignore")
		#title = html_parser.unescape(title)
 		# ignore strange non-html, non-unicode characters
		title = unencode_text(title)
 		if 'published_parsed' in entry and entry["published_parsed"] is not None:
 			datepublished = extract_pubdate(entry["published_parsed"])
 		try:
 			link = entry["link"]
 		except:
 			link = ''
		summarytext = extract_summarytext(entry)
		title = decode_text(title)
		summarytext = decode_text(summarytext)
 		# CREATE TABLE news_exp (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, entrydate DATE NOT NULL, pubdate DATE NOT NULL, title TEXT NOT NULL, summary TEXT NOT NULL, link TEXT NOT NULL);
 		sql = "INSERT INTO news3 VALUES (NULL, CURDATE(), %s, %s, %s, %s)"
 		cur.execute(sql, (datepublished, title, summarytext, link) )





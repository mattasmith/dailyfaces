
# pagerank people and scrape articles for quotes from top people
import MySQLdb as mdb
import urllib2, cookielib, threading
import Queue
from BeautifulSoup import BeautifulSoup
from time import sleep
import nltk
from grabtest4 import *
import pickle

def decode_text(text):
	try:
		cleantext = text.decode('utf8','ignore')
	except:
		print 'Error with decoding %s' % text
		cleantext = ''
	return cleantext

# load rss data from MySQL database
# connect to the mySQL database rssfeeddata
con = mdb.connect('localhost', 'testuser', 'test123', 'rssfeeddata',  charset='utf8')
with con:
	cur = con.cursor(mdb.cursors.DictCursor)
	# get links for each unique article
	cur.execute("SELECT id, link \
		FROM article3 \
		WHERE entrydate='2014-01-30'; ") # get all links to news
	rows = cur.fetchall()





# get all the links for the top people - still to do! can I do it as one sql query?
#with con:
#	cur = con.cursor(mdb.cursors.DictCursor)

webtext = {}
print 'start download'



# grab web text for top links
for i, row in enumerate(rows):
	url = row['link']
	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	request = urllib2.Request(url)
	request.add_header('User-Agent-Matt', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)')   
	cj.add_cookie_header(request)   
	try:
		response = opener.open(request)
		html = response.read()
		response.close()
	except:
		print 'Failed: '+url
	#response = urllib2.urlopen(request)
	#cj.extract_cookies(response, request)  
	

	soup = BeautifulSoup(html)
	webtext[row['id']] = nltk.clean_html(str(soup))
	sleep(0.5)
	print i, len(rows)

# save for experimenting with parsing quotes
#pickle.dump( webtext, open('content4.pkl', 'w'))


with con:
	cur = con.cursor(mdb.cursors.DictCursor)	
	for row in rows:
		rss_id = row['id']
		for quote, quoter in pullquotes(webtext[row['id']]):
			if quote and quoter:
				quote = decode_text(quote)
				quoter = decode_text(quoter)
				#print quote, quoter
				#CREATE TABLE quotes3 (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, rss_id INT NOT NULL, quote TEXT NOT NULL, quoter TEXT NOT NULL);
				sql = "INSERT INTO quotes3 VALUES (NULL, %s, %s, %s)"
				cur.execute(sql, (rss_id, quote, quoter) )












# pagerank people and scrape articles for quotes from top people
import MySQLdb as mdb
import urllib2, cookielib, threading
import Queue
from BeautifulSoup import BeautifulSoup
from time import sleep
import nltk
import pickle
import HTMLParser
import re


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


# given sourcetmp, find the source by looking for capital words
def sourcesearchforward(sourcetmp):
	words = sourcetmp.split()
	source = []
	for word in words:
		if re.match(r'[A-Z]', word):
			word.replace(',','')
			source.append(word)
		else:
			return ' '.join(source)
		if re.search(r'\.', word):
			return ' '.join(source)
	return ' '.join(source)


def sourcesearchreverse(sourcetmp):
	words = sourcetmp.split()
	source = []
	for word in reversed(words):
		if re.search(r'\.', word):
			return ' '.join(source)
		if re.match(r'[A-Z]', word):
			word.replace(',','')
			source.append(word)
		else:
			break
	return ' '.join(reversed(source))

#person = 'Chris Christie'
#with open('testarticle3.txt', 'rU') as f:
#	content = f.read()


def unencode_text(text):
	#print text
	try:
		cleantext = html_parser.unescape(text)
	except:
		print 'Error with escaping %s' % text
		cleantext = ''
	return cleantext


# return all sentences with a quote.
# includes the wrapping sentence - use to get some context?
def pullquotes(content):
	verblist = ['added', 'says', 'wrote', 'said'] # most important last
	quotationlist = []
	for paragraph in content.split('\n'):
		matches = re.findall(r'\.*.*?\".*?\".*?\.*', paragraph) 
		# for each match
		for match in matches:
			source = None
			sourcestatement = None
			completequote = None
			if match:
				# strip out the quote
				# quote may be both in multiple pieces
				# IGNORE PARTIAL QUOTES FOR NOW?
				partialquotes = re.findall(r'\"(.*?)\"', match)
				# process quotes to combine parts put ... in between multiple parts
				completequote = ' ... '.join(partialquotes)
				# note - this will create a many options - need to pick best after running through list
				for verb in verblist:
					# if outerpart in 2 pieces, look for source between the quotes
					if re.search(r'\".*?\".*\".*?\"', match):
						outerparts = re.findall(r'\".*?\"(.*)\".*?\"', match)
						if verb in outerparts[0]:
							sourcestatement = outerparts[0]
					# otherwise if the quote is singular, look for the source both sides of the quote
					else:
						outerparts = re.findall(r'(.*)\".*?\"(.*)', match)
						if verb in outerparts[0][0]:
							sourcestatement = outerparts[0][0] 
						elif verb in outerparts[0][1]:
							sourcestatement = outerparts[0][1]
				
					# look for source around verb, look for capital word in front of verb, if not then behind verb
					if sourcestatement and verb in sourcestatement:
						# use len - can get spaces
						if len(sourcestatement.split(verb)[0]) > 1:
							sourcetmp = sourcestatement.split(verb)[0]
							if sourcetmp.split():
								lastword = sourcetmp.split()[-1]
								if re.match(r'[A-Z]', lastword[0]):
									# source is all the words (working backwards) while capitals and not punctuation
									source = sourcesearchreverse(sourcetmp)
						else:
							sourcetmp = sourcestatement.split(verb)[1]
							if sourcetmp.split():
								firstword = sourcetmp.split()[0]
								if re.match(r'[A-Z]', firstword[0]):
									# source is all the words while capitals and not punctuation	
									source = sourcesearchforward(sourcetmp)
			#print completequote, proxystatement
			if source!=None and completequote!=None:
				source = unencode_text(source)
				completequote = unencode_text(completequote)
				# handle weird html characters
				#source = source.encode('utf8','ignore')
				#source = html_parser.unescape(source)
				# clean source and quote from excess whitespace
				source = source.strip()
				#source.replace('\"','')
				# handle weird html characters
				# completequote = completequote.decode('unicode-escape')
				#completequote = html_parser.unescape(completequote)
				#completequote = completequote.decode('utf8','ignore').encode('ascii', 'ignore')
				completequote = completequote.strip()
				quotationlist.append( (completequote, source) )
	return list(set(quotationlist))



# load rss data from MySQL database
# connect to the mySQL database rssfeeddata
con = mdb.connect('localhost', 'testuser', 'test123', 'rssfeeddata',  charset='utf8')
with con:
	cur = con.cursor(mdb.cursors.DictCursor)
	# get links for each unique article
	cur.execute("SELECT id, link \
		FROM article3 \
		WHERE entrydate='2014-02-23'; ") # get all links to news
	rows = cur.fetchall()


# use this to escape html characters
html_parser = HTMLParser.HTMLParser()

webtext = {}
print 'start download'


# grab web text for top links
for i, row in enumerate(rows):
	# set html content to empty string
	html = ''
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











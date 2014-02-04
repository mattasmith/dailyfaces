
# pagerank people and scrape articles for quotes from top people
import MySQLdb as mdb
import urllib2, cookielib
from BeautifulSoup import BeautifulSoup
from time import sleep
import nltk





def wiki_search(name):
	# assume name is a person, exclude if not
	person_bool = True
	wikiname = None

	# if the name is a string of length 0, then break with person_bool False
	if len(name) == 0:
		person_bool = False
		return person_bool, wikiname

	# format the link, replace underscore with spaces
	url = 'http://en.wikipedia.org/wiki/%s' % name.replace(' ','_')

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
		return person_bool, wikiname

	soup = BeautifulSoup(html)
	webtext = nltk.clean_html(str(soup))
	sleep(0.5)
	# a person if the word born is in the first few paragraphs of wikipedia
	person_bool = 'born' in webtext[:5000] or 'Early life' in webtext[:5000]
	# get the name wikipedia thinks the person is
	wikiname = webtext.split('-')[0].strip()
	# if the wikiname is really long, probably not a name
	if len(wikiname) > 50:
		wikiname = None
	return person_bool, wikiname




# names for unit test
#names = ['Barack Obama', 'Chris Christie', 'Oxfam International', 'Mou.koouej', '']
#
#for name in names:
#	person_bool, wikiname = wiki_search(name)
#	print name, person_bool, wikiname












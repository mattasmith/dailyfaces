
# retrieve top ten people for homepage
import MySQLdb as mdb
import HTMLParser

class person():
	''' 
	Class to store queries of top people and select link, quote, keywords
	'''
	def __init__(self, name, person_id):
		self.name = name
		self.links = None # one link
		self.keywords = None
		self.quote = None # one quote
		self.sources = None
		self.imageurl = None
		self.tagid = name.replace(' ', '').replace('.','').replace('\'','')
		self.person_id = person_id

	def addlinks(self, links):
		''' simple function, take all links '''
		self.links = links

	def getlinks(self):
		return self.links

	def addkeywords(self, keywords):
		''' simple function, takes all keywords '''
		self.keywords = [kw for kw in keywords if kw not in self.name]

	def getkeywords(self):
		return self.keywords

	def addquote(self, quotes):
		''' simple function, takes most recent quote'''
		if quotes:
			self.quote = quotes[0]

	def getquote(self):
		return self.quote

	def addsource(self, sources):
		self.sources = sources

	def getsource(self):
		return self.sources

	def addimage(self, imageurl):
		self.imageurl = imageurl

	def getimage(self):
		return self.imageurl





def find_top_people(date):
	'''
	Function takes a date and
	returns list of the top people
	(as dict with person and people_id keys)
	on that date. 
	'''
	
	con = mdb.connect('localhost', 'testuser', 'test123', 'rssfeeddata')
	with con:
		cur = con.cursor(mdb.cursors.DictCursor)
		# get the top ten people, links, keywords
		cur.execute("SELECT person, imageurl, COUNT(*) AS rank, people_id \
		FROM people3 \
		INNER JOIN map_people3 ON map_people3.people_id=people3.id \
		INNER JOIN article3 ON map_people3.article_id=article3.id \
		WHERE entrydate = %s \
		GROUP BY people3.person \
		ORDER BY rank DESC \
		LIMIT 20; ", (date,) ) # get all links to news
		people_list = cur.fetchall()
	return people_list



def search_top_people(date, keyword):
	'''
	Function takes a date and
	returns list of the top people
	(as dict with person and people_id keys)
	on that date. 
	'''
	
	con = mdb.connect('localhost', 'testuser', 'test123', 'rssfeeddata')
	with con:
		search_re = '.*[[:<:]]'+keyword+'[[:>:]].*' # create the REGEXP to search with
		cur = con.cursor(mdb.cursors.DictCursor)
		# get the top ten people, links, keywords
		cur.execute("SELECT person, imageurl, COUNT(*) AS rank, people_id \
		FROM people3 \
		INNER JOIN map_people3 ON map_people3.people_id=people3.id \
		INNER JOIN article3 ON map_people3.article_id=article3.id \
		WHERE entrydate = %s AND keywords REGEXP %s \
		GROUP BY people3.person \
		ORDER BY rank DESC \
		LIMIT 10; ", (date, search_re) ) # get all links to news # 
		people_list = cur.fetchall()
	return people_list



def list_to_people(date, people_list):
	'''
	Function takes people_id result from SQL query, 
	finds attributes for each person,
	and returns the list as people.
	'''
	con = mdb.connect('localhost', 'testuser', 'test123', 'rssfeeddata')
	toppeople = []
	# for each person
	for i, row in enumerate(people_list):
		name = row['person']
		person_id = row['people_id']
		imageurl = row['imageurl']
		# check the name is utf8 compatible
		try:
			name.encode('utf8')
		except:
			break
		toppeople.append(person(name, person_id)) # create instance of person
		toppeople[i].addimage(imageurl)
		# search for a quote by matching last name
		with con:
			cur = con.cursor(mdb.cursors.DictCursor)
			# get the quotes
			cur.execute("SELECT rss_id, quote, quoter \
			FROM quotes3 \
			WHERE quoter REGEXP '.*[[:<:]]%s[[:>:]].*' \
			ORDER BY rss_id DESC;" % name.split()[-1].replace('\'','\\\'') ) # need to take care of names with 's
			quote_list = cur.fetchall()
		allthequotes = [quote_row['quote'] for quote_row in quote_list]
		toppeople[i].addquote(allthequotes)


		with con:
			cur = con.cursor(mdb.cursors.DictCursor)
			# get the people, links, keywords
			cur.execute("SELECT person, link, source, keywords, title \
			FROM people3 \
			INNER JOIN map_people3 ON map_people3.people_id=people3.id \
			INNER JOIN article3 ON map_people3.article_id=article3.id \
			WHERE entrydate = %s AND people_id=%s; ", (date, row['people_id']) ) # get all links to news
			article_list = cur.fetchall()
		allthekeywords = []
		allthelinks = []
		allthesources = []
		# this will escape html characters that are in the database
		# html characters are now being escaped when feed database, may not need to escape here in future
		html_parser = HTMLParser.HTMLParser()

		for article_row in article_list:
			article_keywords = article_row['keywords'].split()
			allthekeywords += article_keywords
			# check the title is utf8 compatible
			try:
				article_row['title'].encode('utf8')
				if article_row['source']!= 'None' and article_row['source'] not in allthesources and article_row['title']!='':
					allthesources.append(article_row['source'])
					allthelinks.append( (article_row['link'], article_row['title'], article_row['source'].split('.')[0]) )
			except:
				pass
		toppeople[i].addlinks(allthelinks)
		toppeople[i].addkeywords(allthekeywords)
		toppeople[i].addsource(allthesources)


	return toppeople



def peopleinthenews(date='2014-01-14', keyword=None):
	'''
	Function takes date and keywords and returns people
	as instances of the person class. 
	'''
	if not keyword:
		people_list = find_top_people(date)
		toppeople = list_to_people(date, people_list)
		return toppeople

	else:
		people_list = search_top_people(date, keyword)
		toppeople = list_to_people(date, people_list)
		return toppeople



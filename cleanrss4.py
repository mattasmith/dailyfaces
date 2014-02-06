
# download rss data from MySQL database, identify date published, names, keywords and source website

import re
import MySQLdb as mdb
import nltk
import operator
from datetime import datetime
import time
import enchant
from wikifilter import wiki_search


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


def get_place_names():
	# load all world cities, districts, countries (with name length > 1 word)
	con = mdb.connect('localhost', 'testuser', 'test123', 'rssfeeddata')
	with con:
		cur = con.cursor(mdb.cursors.DictCursor)
		cur.execute("SELECT name FROM cities") # get all rss data with text descriptions
		rows = cur.fetchall()
	city_names = [row['name'] for row in rows]
	with con:
		cur = con.cursor(mdb.cursors.DictCursor)
		cur.execute("SELECT name FROM countries") # get all rss data with text descriptions
		rows = cur.fetchall()
	country_names = [row['name'] for row in rows]
	with con:
		cur = con.cursor(mdb.cursors.DictCursor)
		cur.execute("SELECT district FROM districts") # get all rss data with text descriptions
		rows = cur.fetchall()
	district_names = [row['district'] for row in rows]
	place_names = city_names + country_names + district_names
	return place_names


def filter_names(chunk, place_names):
	# use this dictionary to throw out bad names
	word_dict = enchant.Dict("en_US")
	names = []
	# if chunk assigned as a person and the number of words is greater than 1, and less than 4, and chunk is not in place_names
	# I miss some names at the beginning of sentences - nltk wants to split them into separate names
	if len(chunk.leaves())>1 and len(chunk.leaves())<4 and ' '.join([c[0] for c in chunk.leaves()]) not in place_names:
		# if more than one word in the name is in the pyenchant dictionary, ignore name
		# remember to consider lowercase words - uppercase words are in pyenchant!
		num_dict_words = len([w for w in chunk.leaves() if word_dict.check(w[0].lower())])
		if num_dict_words<2:
			name = ' '.join([c[0] for c in chunk.leaves()])
			person_bool, wikiname = wiki_search(name)
			# if a name on wikipedia (or article not found) but no wikiname, use name
			if person_bool == True and wikiname == None:
				names.append(name)
			# if a name on wikipedia (or article not found) and wikiname, use wikiname
			elif person_bool == True and wikiname != None:
				names.append(wikiname)
			# otherwise, filter out name
			else:
				print 'Filtering out %s using Wikipedia' %name
	return names


def extract_names(text, place_names):
	'''  NLTK function to pull out people referenced by two or three names'''
	names = []
	for sent in nltk.sent_tokenize(text):
		for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
			if hasattr(chunk, 'node'):
				if chunk.node=='PERSON':
					names = filter_names(chunk, place_names)
	return names


def extract_keywords(text):
	''' simple function to pull out nouns, exclude names (or exclude words with caps!) '''
	keywords = []
	for sent in nltk.sent_tokenize(text):
		for tagged in nltk.pos_tag(nltk.word_tokenize(sent)):
			if tagged[1] in ['NN', 'NNP', 'JJ']:
				keywords.append(tagged[0])
	return keywords


def extract_newssite(text):
	''' simple function to get newssource from the link '''
	match = re.search(r'http://[\w\.]*\.(\w+\.com).*', row['link'])
	if match:
		return match.group(1)
	match = re.search(r'http://[\w\.]*\.(\w+\.org).*', row['link'])
	if match:
		return match.group(1)
	match = re.search(r'http://[\w\.]*\.(\w+\.ca).*', row['link'])
	if match:
		return match.group(1)
	match = re.search(r'http://[\w\.]*\.(\w+\.co\.uk).*', row['link'])
	if match:
		return match.group(1)
	match = None
	return match



# load rss data from MySQL database
# connect to the mySQL database rssfeeddata
con = mdb.connect('localhost', 'testuser', 'test123', 'rssfeeddata')
with con:
	cur = con.cursor(mdb.cursors.DictCursor)
	cur.execute("SELECT * FROM news3 WHERE summary !=''  AND entrydate='2014-02-06'") # get all rss data with text descriptions
	rows = cur.fetchall()




#######################################################
# this is where I can disambiguate similar names, etc.#
#######################################################

# approach - look through all names, return a dictionary of single names and rss_id mapping them to full names

# get a list of places to filter names against
place_names = get_place_names()

# for each rss story
for row in rows:
	rss_id = row['id']
	entrydate = row['entrydate']
	datepublished = row['pubdate']
	title = decode_text(row['title'])
	keywords = ' '.join(extract_keywords(row['summary']))
	source = extract_newssite(row['link'])
	link = row['link']
	people = extract_names(row['summary'], place_names)
	people = [decode_text(person) for person in people]
	# if there is a person, save rss story as article
	if people:
		with con:
			cur = con.cursor(mdb.cursors.DictCursor)
			# CREATE TABLE article3 (id INT NOT NULL, entrydate DATE NOT NULL, pubdate DATE NOT NULL, title TEXT NOT NULL, keywords TEXT NOT NULL, source TEXT NOT NULL, link TEXT NOT NULL);
			sql = "INSERT INTO article3 VALUES (%s, %s, %s, %s, %s, %s, %s)"
			cur.execute(sql, (rss_id, entrydate, datepublished, title, keywords, source, link) )
		# for each person mentioned in an article, put in people table
		for person in people:
			if person:
				# add to people table if person exists
				with con:
					cur = con.cursor(mdb.cursors.DictCursor)
					sql = "SELECT id, person FROM people3 WHERE person=%s"
					cur.execute(sql, (person,) ) # search for person a
					personsearch = cur.fetchall()
				with con:
					cur = con.cursor(mdb.cursors.DictCursor)
					# if person not exist, add to people
					if not personsearch:
						# CREATE TABLE people3 (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, person TEXT NOT NULL, imageurl TEXT);
						sql = "INSERT INTO people3 VALUES (NULL, %s, NULL)" # could search for image here
						cur.execute(sql, (person,) )
				# add to map_people table
				with con:
					cur = con.cursor(mdb.cursors.DictCursor)
					sql = "SELECT id, person FROM people3 WHERE person=%s"
					cur.execute(sql, (person,) ) # search for person
					personsearch = cur.fetchall()	
				with con:
					cur = con.cursor(mdb.cursors.DictCursor)		
					# CREATE TABLE map_people3 (people_id INT NOT NULL, article_id INT NOT NULL);
					sql = "INSERT INTO map_people3 VALUES (%s, %s)"
					cur.execute(sql, (personsearch[0]['id'], rss_id ) )














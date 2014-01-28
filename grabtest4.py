import re
import HTMLParser
#import nltk

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
	# use this to escape html characters
	html_parser = HTMLParser.HTMLParser()
	for paragraph in content.split('\n'):
		matches = re.findall(r'\.*.*?\".*?\".*?\.*', paragraph) 

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
							lastword = sourcetmp.split()[-1]
							if re.match(r'[A-Z]', lastword[0]):
								# source is all the words (working backwards) while capitals and not punctuation
								source = sourcesearchreverse(sourcetmp)
						else:
							sourcetmp = sourcestatement.split(verb)[1]
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



		




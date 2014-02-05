
'''
Download all the images locally!
'''
import urllib
import MySQLdb as mdb
import urllib2
import json



def bing_search(query, search_type):
    #search_type: Web, Image, News, Video
    key= 'JWtpefyIrl/4JuBGfuywn85RhodEz4P+b5pBHzSaGXg='
    query = urllib.quote(query)
    # create credential for authentication
    user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'
    credentials = (':%s' % key).encode('base64')[:-1]
    auth = 'Basic %s' % credentials
    url = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/'+search_type+'?Query=%27'+query+'%27&Adult=%27'+'Strict'+'%27&ImageFilters=%27'+'Size'+'%3aMedium%27&$top=5&$format=json'
    request = urllib2.Request(url)
    request.add_header('Authorization', auth)
    request.add_header('User-Agent', user_agent)
    request_opener = urllib2.build_opener()
    response = request_opener.open(request)
    response_data = response.read()
    json_result = json.loads(response_data)
    result_list = json_result['d']['results']
    #print result_list
    return result_list
 

def image_search(query):
    #query = "Barack Obama"
    results =  bing_search(query, 'Image')
    try:
        img_url = results[0]['MediaUrl'] # take the top result
    except:
        img_url = None
    return img_url



# load people data from MySQL database
# connect to the mySQL database rssfeeddata
con = mdb.connect('localhost', 'testuser', 'test123', 'rssfeeddata')
with con:
    cur = con.cursor(mdb.cursors.DictCursor)
    cur.execute("SELECT * FROM people3 WHERE imageurl is NULL") # get all people data who do not have a picture
    rows = cur.fetchall()

# for each person without an image, add an image!
for row in rows:
	with con:
		cur = con.cursor(mdb.cursors.DictCursor)
        person = row['person']
        imageurl = image_search(person)
        sql = "UPDATE people3 SET imageurl=%s WHERE id=%s"
        cur.execute(sql, (imageurl, row['id']) )
        print row['id']
        try:
            urllib.urlretrieve(imageurl, "static/images/download/%s.jpg" %  str(row['id']) )
            # shrink image to 1000px max
            #resizeImage("static/images/download/%s.jpg" % str(row['id']) )
        except:
			print 'Unable to download: %s' % row['imageurl']





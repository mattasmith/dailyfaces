

from flask import Flask, render_template, request
import MySQLdb as mdb
import sqlqueries

app = Flask(__name__)
con = mdb.connect('localhost', 'testuser', 'test123', 'rssfeeddata')
currentdate = '2014-02-20' # 2014-02-03 2014-02-27 2014-01-23

@app.route("/")
@app.route("/index.html")
def hello():
	toppeople = sqlqueries.peopleinthenews(currentdate)
	return render_template('index.html', toppeople=toppeople)

@app.route("/db")
def top():
	toppeople = sqlqueries.peopleinthenews(currentdate)
	return toppeople[2].tagid


@app.route('/search.html')
def search():
    keyword = request.args.get('q', None)

    toppeople = sqlqueries.peopleinthenews(currentdate, keyword)   

    return render_template('search.html',
            toppeople=toppeople,
            keyword = keyword)







@app.route("/blocker")
def block():
	return "Blocked!"

@app.route("/<pagename>")
def regularpage(pagename=None):
	"""
	Route not found by the other routes
	"""
	return "You've arrived at " + pagename

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)

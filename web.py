

from flask import Flask, render_template, request
import MySQLdb as mdb
import sqlqueries

app = Flask(__name__)
con = mdb.connect('localhost', 'testuser', 'test123', 'rssfeeddata')

@app.route("/")
@app.route("/index.html")
def hello():
	toppeople = sqlqueries.peopleinthenews('2014-01-27')
	return render_template('index.html', toppeople=toppeople)

@app.route("/db")
def top():
	toppeople = sqlqueries.peopleinthenews('2014-01-27')
	return toppeople[0].name


@app.route('/search.html')
def search():
    keyword = request.args.get('q', None)

    toppeople = sqlqueries.peopleinthenews('2014-01-27', keyword)   

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
    app.run('0.0.0.0', port=8080, debug=True)

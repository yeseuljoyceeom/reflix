from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dbreflix


## HTML 화면 보여주기
@app.route('/')
def mainpage():
    return render_template('index.html')


@app.route('/search')
def searchMovies():
    return render_template('movies.html')


@app.route('/movie')
def movieinfo():
    return render_template('movie.html')


@app.route('/whatsnew')
def newmovies():
    return render_template('whatsnew.html')


@app.route('/leavingsoon')
def leavingsoon():
    return render_template('leavingsoon.html')


@app.route('/board')
def board():
    return render_template('board.html')


@app.route('/contents', methods=["GET"])
def printcontents():
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 28))
    totalContents = db.all_contents.count()
    n_skip = (page - 1) * size
    pageContents = list(db.all_contents.find({}, {"_id": False}).skip(n_skip).limit(size))

    return jsonify({'result': 'success', 'contents': pageContents, 'total': totalContents})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

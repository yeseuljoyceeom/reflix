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


@app.route('/boardpost')
def boardpost():
    return render_template('boardpost.html')


@app.route('/contents', methods=["GET"])
def printcontents():
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 28))
    order = request.args.get('order')
    totalContents = db.totContents.count()
    n_skip = (page - 1) * size

    if order == 'latest':
        pageContents = list(
            db.totContents.find({}, {"_id": False}).sort([('year', -1), ('_id', 1)]).skip(n_skip).limit(size))
    elif order == 'oldest':
        pageContents = list(
            db.totContents.find({}, {"_id": False}).sort([('year', 1), ('_id', 1)]).skip(n_skip).limit(size))
    return jsonify({'result': 'success', 'contents': pageContents, 'total': totalContents})


@app.route('/content', methods=["GET"])
def printcontent():
    id = int(request.args.get('id'))
    content = db.totContents.find_one({"contentId": id}, {"_id": False})

    return jsonify({'result': 'success', 'content': content})


@app.route('/movie_comment', methods=["POST"])
def post_movie_comment():
    contentId = int(request.form["id_give"])
    star = int(request.form["star_give"])
    comment = request.form["comment_give"]
    date = request.form["date_give"]

    db.totContents.update_one({"contentId": contentId},
                              {"$push": {"comment": {"star": star, "text": comment, "date": date}}})
    return jsonify({'result': 'success', 'msg': '리뷰 작성 완료!'})


@app.route('/movie_comment', methods=["GET"])
def read_comment():
    contentId = int(request.args.get("id_give"))
    try:
        comments = db.totContents.find_one({"contentId": contentId})["comment"]
    except KeyError:
        comments = "None"

    return jsonify({'result': 'success', 'comments': comments})


@app.route('/posts', methods=["GET"])
def read_posts():
    page = int(request.args.get('page_give'))
    size = int(request.args.get('size_give'))
    n_skip = (page - 1) * size
    posts = list(db.board.find({}, {"_id": False}).sort([('postId', -1), ('_id', 1)]).skip(n_skip).limit(size))
    total = db.board.count()
    return jsonify({'result': 'success', 'data': posts, 'total': total})


@app.route('/posts', methods=["POST"])
def post_post():
    postId = int(list(db.board.find({}, {"_id": False}))[-1]['postId']) + 1
    title = request.form['title_give']
    content = request.form['content_give']
    date = request.form['date_give']
    doc = {
        'postId': postId,
        'title': title,
        'content': content,
        'date': date
    }
    db.board.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '글 작성 완료!'})


@app.route('/post', methods=["GET"])
def read_post():
    postId = int(request.args.get('id_give'))
    post = db.board.find_one({'postId': postId}, {'_id': False})
    return jsonify({'result': 'success', 'data': post})


@app.route('/board_comment', methods=["POST"])
def post_board_comment():
    postId = int(request.form['id_give'])
    comment = request.form['comment_give']
    date = request.form['date_give']

    db.board.update_one({"postId": postId},
                        {"$push": {"comment": {"comment": comment, "date": date}}})
    return jsonify({'result': 'success', 'msg': '댓글 작성 완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

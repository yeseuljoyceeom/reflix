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
    keyword = request.args.get('keyword')
    category = int(request.args.get('category', 1))
    n_skip = (page - 1) * size

    def return_data(ctgr, ord):
        if ctgr == 2:
            ctgr = '영화'
        elif ctgr == 3:
            ctgr = '드라마'
        elif ctgr == 4:
            ctgr = '쇼'
        elif ctgr == 5:
            ctgr = '다큐멘터리'
        elif ctgr == 6:
            ctgr = '애니메이션'

        if ord == 1:
            ord = 1
        else:
            ord = -1

        result = list(db.totContents.find({'$and': [{'type': {'$regex': ctgr}},
                                                    {'$or': [{'title': {'$regex': keyword}},
                                                             {'cast': {'$regex': keyword}},
                                                             {'director': {'$regex': keyword}}]}]},
                                          {"_id": False}).sort(
            [('year', ord), ('_id', 1)]).skip(n_skip).limit(size))
        totalContents = len(list(db.totContents.find({'$and': [{'type': {'$regex': ctgr}},
                                                               {'$or': [{'title': {'$regex': keyword}},
                                                                        {'cast': {'$regex': keyword}},
                                                                        {'director': {'$regex': keyword}}]}]},
                                                     {"_id": False})))
        return [totalContents, result]

    # return data w/o keyword
    def return_data_wo_key(ctgr, ord):
        if ctgr == 2:
            ctgr = '영화'
        elif ctgr == 3:
            ctgr = '드라마'
        elif ctgr == 4:
            ctgr = '쇼'
        elif ctgr == 5:
            ctgr = '다큐멘터리'
        elif ctgr == 6:
            ctgr = '애니메이션'

        if ord == 1:
            ord = 1
        else:
            ord = -1

        result = list(db.totContents.find({'type': {'$regex': ctgr}}, {"_id": False}).sort(
            [('year', ord), ('_id', 1)]).skip(n_skip).limit(size))
        totalContents = len(list(db.totContents.find({'type': {'$regex': ctgr}}, {"_id": False})))

        return [totalContents, result]

    if keyword != '':
        if order == 'latest':
            if category == 1:
                pageContents = list(
                    db.totContents.find({'$or': [{'title': {'$regex': keyword}}, {'cast': {'$regex': keyword}},
                                                 {'director': {'$regex': keyword}}]}, {"_id": False}).sort(
                        [('year', -1), ('_id', 1)]).skip(n_skip).limit(size))
                totalContents = db.totContents.count(
                    {'$or': [{'title': {'$regex': keyword}}, {'cast': {'$regex': keyword}},
                             {'director': {'$regex': keyword}}]})
            elif category == 2:
                pageContents = return_data(2, -1)[1]
                totalContents = return_data(2, -1)[0]
            elif category == 3:
                pageContents = return_data(3, -1)[1]
                totalContents = return_data(3, -1)[0]
            elif category == 4:
                pageContents = return_data(4, -1)[1]
                totalContents = return_data(4, -1)[0]
            elif category == 5:
                pageContents = return_data(5, -1)[1]
                totalContents = return_data(5, -1)[0]
            elif category == 6:
                pageContents = return_data(6, -1)[1]
                totalContents = return_data(6, -1)[0]

        elif order == 'oldest':
            if category == 1:
                pageContents = list(
                    db.totContents.find({'$or': [{'title': {'$regex': keyword}}, {'cast': {'$regex': keyword}},
                                                 {'director': {'$regex': keyword}}]}, {"_id": False}).sort(
                        [('year', 1), ('_id', 1)]).skip(n_skip).limit(size))
                totalContents = db.totContents.count(
                    {'$or': [{'title': {'$regex': keyword}}, {'cast': {'$regex': keyword}},
                             {'director': {'$regex': keyword}}]})
            elif category == 2:
                pageContents = return_data(2, 1)[1]
                totalContents = return_data(2, 1)[0]
            elif category == 3:
                pageContents = return_data(3, 1)[1]
                totalContents = return_data(3, 1)[0]
            elif category == 4:
                pageContents = return_data(4, 1)[1]
                totalContents = return_data(4, 1)[0]
            elif category == 5:
                pageContents = return_data(5, 1)[1]
                totalContents = return_data(5, 1)[0]
            elif category == 6:
                pageContents = return_data(6, 1)[1]
                totalContents = return_data(6, 1)[0]
    else:
        if order == 'latest':
            if category == 1:
                pageContents = list(
                    db.totContents.find({}, {"_id": False}).sort([('year', -1), ('_id', 1)]).skip(n_skip).limit(size))
                totalContents = db.totContents.count({})
            elif category == 2:
                pageContents = return_data_wo_key(2, -1)[1]
                totalContents = return_data_wo_key(2, -1)[0]
            elif category == 3:
                pageContents = return_data_wo_key(3, -1)[1]
                totalContents = return_data_wo_key(3, -1)[0]
            elif category == 4:
                pageContents = return_data_wo_key(4, -1)[1]
                totalContents = return_data_wo_key(4, -1)[0]
            elif category == 5:
                pageContents = return_data_wo_key(5, -1)[1]
                totalContents = return_data_wo_key(5, -1)[0]
            elif category == 6:
                pageContents = return_data_wo_key(6, -1)[1]
                totalContents = return_data_wo_key(6, -1)[0]
        elif order == 'oldest':
            if category == 1:
                pageContents = list(
                    db.totContents.find({}, {"_id": False}).sort([('year', 1), ('_id', 1)]).skip(n_skip).limit(size))
                totalContents = db.totContents.count({})
            elif category == 2:
                pageContents = return_data_wo_key(2, 1)[1]
                totalContents = return_data_wo_key(2, 1)[0]
            elif category == 3:
                pageContents = return_data_wo_key(3, 1)[1]
                totalContents = return_data_wo_key(3, 1)[0]
            elif category == 4:
                pageContents = return_data_wo_key(4, 1)[1]
                totalContents = return_data_wo_key(4, 1)[0]
            elif category == 5:
                pageContents = return_data_wo_key(5, 1)[1]
                totalContents = return_data_wo_key(5, 1)[0]
            elif category == 6:
                pageContents = return_data_wo_key(6, 1)[1]
                totalContents = return_data_wo_key(6, 1)[0]

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

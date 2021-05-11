import jwt
import hashlib
import re
from functools import wraps
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for, g, make_response, flash

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('mongodb://yeseul:d665112@localhost',27017)
# client = MongoClient('localhost', 27017)
db = client.dbreflix

# jwt secret key
SECRET_KEY = 'cherry tomato'
COOKIE_KEY = 'token_give'

# secret_key for flash()
app.secret_key = 'flash_secret'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 쿠키에서 token_give 가져오기
        token_receive = request.cookies.get(COOKIE_KEY)
        # print('token_receive :', token_receive)

        if token_receive is None:
            # token이 없는 경우
            flash('로그인 후 이용해 주세요')
            return redirect(url_for('login'))

        try:
            # 전달받은 token이 위조되었는지 확인 (단방향이기 때문에 비밀번호와 마찬가지로 해쉬처리하여 동일한지 비교)
            # SECRET_KEY를 모르면 동일한 해쉬를 만들 수 없음
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        except jwt.InvalidTokenError:
            # 토큰 없거나 만료되었거나 올바르지 않은 경우 로그인 페이지로 이동
            flash('로그인 후 이용해 주세요')
            return redirect(url_for('login'))

        # g는 각각의 request 내에서만 값이 유효한 스레드 로컬 변수입니다.
        # 사용자의 요청이 동시에 들어오더라도 각각의 request 내에서만 g 객체가 유효하기 때문에 사용자 ID를 저장해도 문제가 없습니다.
        g.user = db.user.find_one({'userId': payload["id"]})

        # 로그인 성공시 다음 함수 실행
        return f(*args, **kwargs)

    return decorated_function


#################################
# HTML 응답 API
#################################
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
@login_required
def boardpost():
    return render_template('boardpost.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login')
def login():
    return render_template('login.html')


#################################
# JSON 응답 API
#################################

# 영화검색페이지 영화리스트
@app.route('/contents', methods=["GET"])
def printcontents():
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 28))
    order = int(request.args.get('order'))
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

        if ord == 1 or ord == -1:
            result = list(db.totContents.find({'$and': [{'type': {'$regex': ctgr}},
                                                        {'$or': [{'title': {'$regex': keyword}},
                                                                 {'cast': {'$regex': keyword}},
                                                                 {'director': {'$regex': keyword}}]}]},
                                              {"_id": False}).sort(
                [('year', ord), ('_id', 1)]).skip(n_skip).limit(size))

        elif ord == 3:
            result = list(db.totContents.find({'$and': [{'type': {'$regex': ctgr}},
                                                        {'$or': [{'title': {'$regex': keyword}},
                                                                 {'cast': {'$regex': keyword}},
                                                                 {'director': {'$regex': keyword}}]}]},
                                              {"_id": False}).sort(
                [('average', -1), ('_id', 1)]).skip(n_skip).limit(size))

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

        if ord == 1 or ord == -1:
            result = list(db.totContents.find({'type': {'$regex': ctgr}}, {"_id": False}).sort(
                [('year', ord), ('_id', 1)]).skip(n_skip).limit(size))
        elif ord == 3:
            result = list(db.totContents.find({'type': {'$regex': ctgr}}, {"_id": False}).sort(
                [('average', -1), ('_id', 1)]).skip(n_skip).limit(size))

        totalContents = len(list(db.totContents.find({'type': {'$regex': ctgr}}, {"_id": False})))

        return [totalContents, result]

    if keyword != '':
        if order == 1:
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

        elif order == 2:
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

        elif order == 3:
            if category == 1:
                pageContents = list(
                    db.totContents.find({'$or': [{'title': {'$regex': keyword}}, {'cast': {'$regex': keyword}},
                                                 {'director': {'$regex': keyword}}]}, {"_id": False}).sort(
                        [('average', -1), ('_id', 1)]).skip(n_skip).limit(size))
                totalContents = db.totContents.count(
                    {'$or': [{'title': {'$regex': keyword}}, {'cast': {'$regex': keyword}},
                             {'director': {'$regex': keyword}}]})
            elif category == 2:
                pageContents = return_data(2, 3)[1]
                totalContents = return_data(2, 3)[0]
            elif category == 3:
                pageContents = return_data(3, 3)[1]
                totalContents = return_data(3, 3)[0]
            elif category == 4:
                pageContents = return_data(4, 3)[1]
                totalContents = return_data(4, 3)[0]
            elif category == 5:
                pageContents = return_data(5, 3)[1]
                totalContents = return_data(5, 3)[0]
            elif category == 6:
                pageContents = return_data(6, 3)[1]
                totalContents = return_data(6, 3)[0]
    else:
        if order == 1:
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
        elif order == 2:
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
        elif order == 3:
            if category == 1:
                pageContents = list(
                    db.totContents.find({}, {"_id": False}).sort([('average', -1), ('_id', 1)]).skip(n_skip).limit(size))
                totalContents = db.totContents.count({})
            elif category == 2:
                pageContents = return_data_wo_key(2, 3)[1]
                totalContents = return_data_wo_key(2, 3)[0]
            elif category == 3:
                pageContents = return_data_wo_key(3, 3)[1]
                totalContents = return_data_wo_key(3, 3)[0]
            elif category == 4:
                pageContents = return_data_wo_key(4, 3)[1]
                totalContents = return_data_wo_key(4, 3)[0]
            elif category == 5:
                pageContents = return_data_wo_key(5, 3)[1]
                totalContents = return_data_wo_key(5, 3)[0]
            elif category == 6:
                pageContents = return_data_wo_key(6, 3)[1]
                totalContents = return_data_wo_key(6, 3)[0]

    return jsonify({'result': 'success', 'contents': pageContents, 'total': totalContents})


# 영화 개별페이지
@app.route('/content', methods=["GET"])
def printcontent():
    id = int(request.args.get('id'))
    content = db.totContents.find_one({"contentId": id}, {"_id": False})
    try:
        comments = sorted(content['comment'], key=lambda x: x['like'], reverse=True)
    except KeyError:
        comments = None

    return jsonify({'result': 'success', 'content': content, 'comments':comments})


# 영화 개별페이지 댓글 저장
@app.route('/movie_comment', methods=["POST"])
@login_required
def post_movie_comment():
    contentId = int(request.form["id_give"])
    star = int(request.form["star_give"])
    comment = request.form["comment_give"]
    date = request.form["date_give"]
    like = int(request.form['like_give'])
    try:
        commentId = len(db.totContents.find_one({"contentId": contentId})['comment']) + 1
    except KeyError:
        commentId = 1

    user = g.user['nickname']

    db.totContents.update_one({"contentId": contentId},
                              {"$push": {"comment": {"user": user, "star": star, "text": comment, "date": date, 'like': like, 'commentId':commentId}}})

    # 별점평균 db에 없데이트
    temp = db.totContents.find_one({"contentId": contentId})
    cmmts = temp['comment']
    n = len(cmmts)
    if n > 0:
        cnt = 0
        for cmmt in cmmts:
            cnt += cmmt['star']
        average = round(cnt / len(cmmts), 2)
        print(average)
    db.totContents.update_one({"contentId": contentId}, {"$set": {"average": average}})

    return jsonify({'result': 'success', 'msg': '리뷰 작성 완료!'})

#댓글 좋아요기능
@app.route('/movie_comment_like', methods=["POST"])
@login_required
def movie_comment_like():
    commentId = int(request.form['commentId_give'])
    contentId = int(request.form['contentId_give'])
    db.totContents.update_one({"contentId": contentId, "comment.commentId": commentId},{"$inc":{"comment.$.like": 1}})
    return jsonify({'result': 'success'})

# 영화 개별페이지 댓글 보여주기
# @app.route('/movie_comment', methods=["GET"])
# def read_comment():
#     contentId = int(request.args.get("id_give"))
#     try:
#         comments = db.totContents.find_one({"contentId": contentId})["comment"]
#     except KeyError:
#         comments = "None"
#
#     return jsonify({'result': 'success', 'comments': comments})


# 자유게시판 글리스트
@app.route('/posts', methods=["GET"])
def read_posts():
    page = int(request.args.get('page_give'))
    size = int(request.args.get('size_give'))
    n_skip = (page - 1) * size
    posts = list(db.board.find({}, {"_id": False}).sort([('postId', -1), ('_id', 1)]).skip(n_skip).limit(size))
    total = db.board.count()
    return jsonify({'result': 'success', 'data': posts, 'total': total})


#새로운 게시글 작성
@app.route('/posts', methods=["POST"])
@login_required
def post_post():
    postId = int(list(db.board.find({}, {"_id": False}))[-1]['postId']) + 1
    title = request.form['title_give']
    content = request.form['content_give']
    date = request.form['date_give']

    user = g.user['nickname']
    userId = g.user['userId']

    doc = {
        'postId': postId,
        'title': title,
        'content': content,
        'date': date,
        'user': user,
        'userId': userId
    }
    db.board.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '글 작성 완료!'})


# 자유게시판 글 개별페이지
@app.route('/post', methods=["GET"])
def read_post():
    postId = int(request.args.get('id_give'))
    post = db.board.find_one({'postId': postId}, {'_id': False})
    return jsonify({'result': 'success', 'data': post})


# 게시글 댓글 저장
@app.route('/board_comment', methods=["POST"])
@login_required
def post_board_comment():
    postId = int(request.form['id_give'])
    comment = request.form['comment_give']
    date = request.form['date_give']

    user = g.user['nickname']

    db.board.update_one({"postId": postId},
                        {"$push": {"comment": {'user': user, "comment": comment, "date": date}}})
    return jsonify({'result': 'success', 'msg': '댓글 작성 완료!'})


#게시글 삭제
@app.route('/delete_post', methods=["POST"])
def delete_post():
    postId_receive = int(request.form['postId_give'])
    db.board.delete_one({'postId': postId_receive})

    return jsonify({'result': 'success', 'msg': '삭제 완료'})


#게시글 수정
@app.route('/update_post', methods=["POST"])
def update_post():
    postId_receive = int(request.form['postId_give'])
    updated_content = request.form['updated_content']
    updated_title = request.form['updated_title']

    db.board.update_one({'postId': postId_receive}, {'$set': {"content": updated_content, 'title': updated_title}})

    return jsonify({'result': 'success', 'msg': '수정 완료'})


# 로그인, 회원가입, 로그아웃
@app.route('/confirmId', methods=["GET"])
def confirmId():
    p = re.compile('^[a-z0-9]{6,}')
    id = request.args.get('id_give')

    if p.match(id) is None:
        return jsonify({'result': 'fail', 'msg': '6자 이상의 영문 혹은 영문과 숫자를 조합하여 아이디를 입력해주세요.'})

    user = list(db.user.find({'userId': id}, {'_id': False}))
    if len(user) != 0:
        return jsonify({'result': 'fail', 'msg': '중복된 아이디입니다.'})

    return jsonify({'result': 'success', 'msg': '사용 가능한 아이디입니다🎉'})


@app.route('/signup', methods=["POST"])
def signup():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    # pw를 sha256 방법(단방향)으로 암호화
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'userId': id_receive, 'userPw': pw_hash, 'nickname': nickname_receive})

    return jsonify({'result': 'success', 'msg': '🎉 회원가입을 완료했습니다.🎉'})


@app.route('/login_api', methods=['POST'])
def login_api():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # pw를 sha256 방법(단방향)으로 암호화
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된 pw을 가지고 해당 유저를 찾기
    user = db.user.find_one({'userId': id_receive, 'userPw': pw_hash})

    if user is not None:
        # jwt 토큰 발급
        payload = {
            'id': user['userId'],  # user id
            'exp': datetime.utcnow() + timedelta(minutes=60)  # 만료 시간
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        print(f'token : {token}')
        res = make_response(jsonify({'result': 'success', 'msg': f'{user["nickname"]}님 안녕하세요 🙇🏻‍♂️'}))

        # set cookie
        res.set_cookie(COOKIE_KEY, token)
        return res
    else:
        return jsonify({'result': 'fail', 'msg': '아이디와 비밀번호를 확인해 주세요 😓'})


#로그인 했는지 안했는지 확인, 했다면 유저 정보 보내기
@app.route('/check_if_login', methods=["GET"])
@login_required
def check_if_login():
    user = g.user['nickname']
    userId = g.user['userId']

    return jsonify({'result': 'success', 'user': user, 'userId': userId})


@app.route('/logout', methods=["POST"])
def logout():
    res = make_response(jsonify({'result': 'success', 'msg': '👋로그아웃 완료👋'}))
    # cookie 삭제
    res.delete_cookie(COOKIE_KEY)

    return res



@app.route('/get_leavingsoon', methods=["GET"])
def get_leavingsoon():
    data = list(db.leavingsoon.find({}, {"_id": False}).sort([('d_leaving', 1), ('_id', 1)]))

    return jsonify({'result': 'success', 'data': data})


@app.route('/get_whatsnew', methods=["GET"])
def get_whatsnew():
    data = list(db.whatsnew.find({}, {"_id": False}).sort([('d_release', 1), ('_id', 1)]))

    return jsonify({'result': 'success', 'data': data})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

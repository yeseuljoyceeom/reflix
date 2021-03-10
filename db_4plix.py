import requests, urllib.request, urllib.parse
from bs4 import BeautifulSoup

from pymongo import MongoClient

localclient = MongoClient('localhost', 27017)
client = MongoClient('mongodb://yeseul:d665112@3.35.218.93', 27017)
localdb = localclient.dbreflix
db = client.dbreflix

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}


def get_netflix_list():
    for i in range(1, 9700):
        try:

            url = 'https://www.4flix.co.kr/board/netflix/' + str(i)
            data = requests.get(url, headers=headers)
            soup = BeautifulSoup(data.text, 'html.parser')
            title = soup.select_one("#card > div.text-block > h1").text.split("(")[0]
            year = soup.select_one("#card > div.text-block > h1").text.split("(")[1].split(")")[0]
            type = soup.select_one("#card > div.text-block > h3:nth-child(3)").text

            doc = {
                'title': title,
                'year': year,
                'type': type
            }
            print(title, year, type)
            db.temp.insert_one(doc)

        except:
            continue

    # 중복값이 없는 뉴컬렉션
    cursor = db.temp.aggregate([
        {"$group": {
            "_id": "$title",
            "count": {"$sum": 1},
            "doc": {"$first": "$$ROOT"}
        }
        },
        {"$replaceRoot": {"newRoot": "$doc"}},
        {"$out": "fourflix"}
    ])


# 다음에 재검색해서 나머지 정보들 가져오기
# 검색하기 쉽게 우선 데이터를 드라마, 영화, 쇼로 나눠 놓는
def classify_type():
    contents = []
    """types = list(db.movies.aggregate([
        {"$group": {
            "_id": "$type",
        }}
    ]))

    for type in types:
        print(type["_id"])"""

    for content in contents:
        if content["type"][:2] == "영화":
            db.movies.insert_one(content)
        elif content["type"][:1] == "쇼":
            db.shows.insert_one(content)
        elif content["type"][:3] == "드라마":
            db.dramas.insert_one(content)
        else:
            db.unknown.insert_one(content)


# 영화제목으로 다음에 검색해서 코드번호를 가져와서
# 다음영화사이트에 코드번호로 재검색
# 나머지 정보들 가져오기
def getmovieinfo():
    movies = ['겟아웃', '시신령:음양사', '싱린의원']
    cnt = 5368
    base_url = "https://search.daum.net/search?w=tot&DA=YZR&t__nil_searchbox=btn&sug=&sugo=&sq=&o=&q="

    for m in movies:
        # for i in range(10):
        if len(list(db.totContents.find({"title": {"$regex": m}}, {'_id': False}))) == 0:
            title = m
            data = requests.get(base_url + urllib.parse.quote(title), headers=headers)
            soup = BeautifulSoup(data.text, 'html.parser')

            try:
                url = soup.select_one("#movieTitle > a")["href"]
                info = requests.get(url, headers=headers)
                ssoup = BeautifulSoup(info.text, 'html.parser')

                try:
                    thumbnail = soup.select_one("#nmovie_img_0 > a > img")["src"]
                except:
                    thumbnail = "None"
                    pass

                try:
                    country = (soup.select_one(
                        "#movieEColl > div.coll_cont > div > div.info_movie > div.wrap_cont > dl:nth-child(2) > dd.cont").text.split(
                        '|'))[0].lstrip().split(' ')[0].strip()
                except:
                    country = "None"
                    pass

                try:
                    genre = (soup.select_one(
                        "#movieEColl > div.coll_cont > div > div.info_movie > div.wrap_cont > dl:nth-child(2) > dd.cont").text.split(
                        '|'))[1].lstrip().split(' ')[0].strip()
                except:
                    genre = "None"
                    pass

                try:
                    runtime = (soup.select_one(
                        "#movieEColl > div.coll_cont > div > div.info_movie > div.wrap_cont > dl:nth-child(2) > dd.cont").text.split(
                        '|'))[-1].split('분')[0].strip()
                except:
                    runtime = "None"
                    pass

                try:
                    director = soup.select_one(
                        "#movieEColl > div.coll_cont > div > div.info_movie > div.wrap_cont > dl:nth-child(3) > dd > a").text
                except:
                    director = "None"
                    pass

                try:
                    cast = soup.select_one(
                        "#movieEColl > div.coll_cont > div > div.info_movie > div.wrap_cont > dl:nth-child(4) > dd").text.split(
                        '더보기')[0].strip()
                except:
                    cast = "None"
                    pass

                try:
                    desc = ssoup.select_one(
                        "#mainContent > div > div.box_detailinfo > div.detail_basicinfo > div > div > div").text.strip()
                except:
                    desc = "None"
                    pass

                try:
                    year = soup.select_one("#movieTitle > span").text.split(',')[1].split('제작')[0].strip()
                except:
                    year = "None"
                    pass

            except:
                country = "None"
                genre = "None"
                runtime = "None"
                director = "None"
                cast = "None"
                desc = "None"
                thumbnail = "None"
                year = "None"

            finally:
                doc = {
                    'title': title,
                    'type': '영화',
                    'country': country,
                    'genre': genre,
                    'runtime': runtime,
                    'director': director,
                    'cast': cast,
                    'desc': desc,
                    'thumbnail': thumbnail,
                    'contentId': cnt,
                    'year': year
                }

            db.whatsnew.insert_one(doc)
            localdb.whatsnew.insert_one(doc)
            print(doc)
            cnt += 1



def getdramainfo():
    dramas = ['좋아하면 울리는 2', '나빌레라']
    cnt = 5371

    base_url = "https://search.daum.net/search?w=tot&DA=YZR&t__nil_searchbox=btn&sug=&sugo=&sq=&o=&q="
    for d in dramas:
        if len(list(db.totContents.find({"title": {"$regex": d}}, {'_id': False}))) != 0:
            continue
        try:
            title = d
            data = requests.get(base_url + urllib.parse.quote(title), headers=headers)
            soup = BeautifulSoup(data.text, 'html.parser')

            try:
                thumbnail = soup.select_one("#tv_program > div.info_cont > div.wrap_thumb > a > img")["src"][2:]
                thumbnail = "https://" + thumbnail
            except:
                thumbnail = "None"
                pass

            try:
                country = soup.select_one(
                    "#tvpColl > div.coll_cont > div > div.head_cont > div > span:nth-child(2)").text
                if country == '드라마':
                    country = '한국드라마'
            except:
                country = "None"
                pass

            try:
                year = soup.select_one(
                    "#tvpColl > div.coll_cont > div > div.head_cont > div > span:nth-child(4)").text.split('.')[0]

            except:
                year = "None"
                pass

            try:
                cast_list = soup.select("#tv_program > div.wrap_col.castingList.lst > ul li")
                temp = []
                for c in cast_list:
                    name = c.select_one("span.sub_name > a").text.strip()
                    temp.append(name)

                if len(temp) != 0:
                    cast = ','.join(temp)
                else:
                    cast = "None"
            except:
                cast = "None"
                pass

            try:
                desc = soup.select_one("#tv_program > div.info_cont > dl:nth-child(3) > dd").text
            except:
                desc = "None"
                pass

        except:
            country = "None"
            thumbnail = "None"
            cast = "None"
            desc = "None"
            year = 'None'

        finally:
            doc = {
                'title': title,
                'type': '드라마',
                'country': country,
                'thumbnail': thumbnail,
                'cast': cast,
                'desc': desc,
                'year': year,
                'contentId': cnt
            }

        db.whatsnew.insert_one(doc)
        localdb.whatsnew.insert_one(doc)
        print(doc)
        cnt += 1




# db.collection.update_many({},{"$rename":{"oldName":"newName"}}) renmae field
# db.collection.update_many({},{"$unset":{"filedName":1}}) delete field

# leaving soon
# dramas = ['신이라 불리는 사나이', '낮과밤','카인과 아벨']
# animation = ['요괴워치', '이나 미나 디카', '로보카 폴리', '오스카의 오아시스']

# temp = db.leavingsoon.find()
# localdb.leavingsoon.insert_many(temp)

# what's new



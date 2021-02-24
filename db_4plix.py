import requests, urllib.request, urllib.parse
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dbreflix

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}


def get_info():
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


contents = list(db.fourflix.find())


# 다음에 재검색해서 나머지 정보들 가져오기
# 검색하기 쉽게 우선 데이터를 드라마, 영화, 쇼로 나눠 놓는
def classify_type():
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
    movies = list(db.movies.find())
    base_url = "https://search.daum.net/search?w=tot&DA=YZR&t__nil_searchbox=btn&sug=&sugo=&sq=&o=&q="

    for movie in movies:
        title = movie["title"]
        data = requests.get(base_url + urllib.parse.quote(title), headers=headers)
        soup = BeautifulSoup(data.text, 'html.parser')

        try:
            code = soup.select_one("#movieTitle > a")["href"].split("=")[1]
            movie_url = "https://movie.daum.net/moviedb/main?movieId="
            info = requests.get(movie_url + code, headers=headers)
            ssoup = BeautifulSoup(info.text, 'html.parser')

            try:
                thumbnail = soup.select_one("#nmovie_img_0 > a > img")["src"]
            except:
                thumbnail = "None"
                pass

            try:
                country = ssoup.select_one(
                    "#mArticle > div.detail_movie.detail_main > div.movie_detail > div.movie_basic > div.main_detail > div.detail_summarize > div > dl:nth-child(2) > dd:nth-child(3)").text
            except:
                country = "None"
                pass

            try:
                genre = ssoup.select_one(
                    "#mArticle > div.detail_movie.detail_main > div.movie_detail > div.movie_basic > div.main_detail > div.detail_summarize > div > dl:nth-child(2) > dd.txt_main").text
            except:
                genre = "None"
                pass

            try:
                runtime = ssoup.select_one(
                    "#mArticle > div.detail_movie.detail_main > div.movie_detail > div.movie_basic > div.main_detail > div.detail_summarize > div > dl:nth-child(3) > dd:nth-last-child(1)").text.split(
                    "분")[0].strip()
            except:
                runtime = "None"
                pass

            try:
                director = ssoup.select_one(
                    "#mArticle > div.detail_movie.detail_main > div.movie_detail > div.movie_basic > div.main_detail > div.detail_summarize > div > dl:nth-child(4) > dd:nth-child(2) > a").text
            except:
                director = "None"
                pass

            try:
                cast = ssoup.select_one(
                    "#mArticle > div.detail_movie.detail_main > div.movie_detail > div.movie_basic > div.main_detail > div.detail_summarize > div > dl:nth-child(4) > dd:nth-child(4)").text.split(
                    "주연")[1].strip()
                cast = ''.join(cast.split())
            except:
                cast = "None"
                pass

            try:
                desc = ssoup.select_one(
                    "#mArticle > div.detail_movie.detail_main > div.movie_detail > div.movie_basic > div.main_detail > div.desc_movie > p").text.strip()
            except:
                desc = "None"
                pass

        except:
            country = "None"
            genre = "None"
            runtime = "None"
            director = "None"
            cast = "None"
            desc = "None"
            thumbnail = "None"

        finally:
            db.movies.update_one({"title": title}, {"$set": {"country": country}})
            db.movies.update_one({"title": title}, {"$set": {"genre": genre}})
            db.movies.update_one({"title": title}, {"$set": {"runtime": runtime}})
            db.movies.update_one({"title": title}, {"$set": {"director": director}})
            db.movies.update_one({"title": title}, {"$set": {"cast": cast}})
            db.movies.update_one({"title": title}, {"$set": {"desc": desc}})
            db.movies.update_one({"title": title}, {"$set": {"thumbnail": thumbnail}})


"""        try:
            data = requests.get(base_url + urllib.parse.quote(title), headers=headers)
            soup = BeautifulSoup(data.text, 'html.parser')
            info = soup.select_one(
                "#movieEColl > div.coll_cont > div > div.info_movie > div.wrap_cont > dl:nth-child(2) > dd.cont").text
            # movieEColl > div.coll_cont > div > div.info_movie > div.wrap_cont.type_longtit5 > dl:nth-child(2) > dd.cont

            country = info.lstrip().split("|")[0].split(" ")[0]
            genre = info.split("|")[1].lstrip().split("|")[0].split(" ")[0]
            runtime = info[-6:-2].strip()

            if not country.isalpha():
                country = "None"
            if not genre.isalpha():
                genre = "None"
            if runtime.isdigit():
                runtime = int(runtime)
            else:
                runtime = "None"

        except:
            country = "None"
            genre = "None"
            runtime = "None"

        finally:
            db.movies.update_one({"title": title}, {"$set": {"country": country}})
            db.movies.update_one({"title": title}, {"$set": {"genre": genre}})
            db.movies.update_one({"title": title}, {"$set": {"runtime": runtime}})"""


# NB. Original query string below. It seems impossible to parse and
# reproduce query strings 100% accurately so the one below is given
# in case the reproduced version is not "correct".
# response = requests.get('https://search.daum.net/qsearch?mk=YDDAQ8DNoAPnZ4Ux7k%40jmAAAAAk&uk=YDDAQ8DNoAPnZ4Ux7k%40jmAAAAAk&q=95073.json&viewtype=json&w=movie&m=comment', headers=headers)


def getinfo():
    shows = list(db.shows.find())
    base_url = "https://search.daum.net/search?w=tot&DA=YZR&t__nil_searchbox=btn&sug=&sugo=&sq=&o=&q="
    for show in shows:
        try:
            title = show["title"]
            data = requests.get(base_url + urllib.parse.quote(title), headers=headers)
            soup = BeautifulSoup(data.text, 'html.parser')

            try:
                thumbnail = soup.select_one("#tv_program > div.info_cont > div.wrap_thumb > a > img")["src"][2:]
                thumbnail = "https://" + thumbnail
            except:
                thumbnail = "None"
                pass

            try:
                category = soup.select_one(
                    "#tvpColl > div.coll_cont > div > div.head_cont > div > span:nth-child(2)").text
            except:
                country = "None"
                pass

            try:
                cast_list = soup.select("#tv_program > div.wrap_col.castingList.lst > ul li")
                temp = []
                for c in cast_list:
                    name = c.select_one("span.txt_name > a").text.strip()
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
            category = "None"
            thumbnail = "None"
            cast = "None"
            desc = "None"

        finally:
            db.shows.update_one({"title": title}, {"$set": {"category": category}})
            db.shows.update_one({"title": title}, {"$set": {"thumbnail": thumbnail}})
            db.shows.update_one({"title": title}, {"$set": {"cast": cast}})
            db.shows.update_one({"title": title}, {"$set": {"desc": desc}})


# db.collection.update_many({},{"$rename":{"oldName":"newName"}}) renmae field
# db.collection.update_many({},{"$unset":{"filedName":1}}) delete field


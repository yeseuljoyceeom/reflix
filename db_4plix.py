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

drama = ['도시남녀의 사랑법', '경우의 수', '상견니', '첫사랑의 멜로디', '열여덟의 순간', '김비서가 왜그럴까', '백일의 낭군님', '디어 마이 프렌즈', '애타는 로맨스', '안녕? 나야!',
         'the k2', '보이스 1', '모범형사', '아는 와이프', '터널', '리갈 하이', '우아한 친구들']
movie = ['트와일라잇', '죽지않는 인간들의 밤', '적선인 흑마살수', '365일', '킹 아서: 제왕의 검', '날씨의 아이', '목소리의 형태', '조작된 도시', '너의 결혼식', '컨저링',
         '탐정 더 비기닝', '문신을 한 신부님', '뉴문', '마션', '아가씨', '인헤리턴스', '시간 이탈자', '모노노케 히메', '신비한 동물사전', '신과 함께 인과 연', '레베카',
         '브레이킹 던', '나의 소녀시대', '너의 이름은', '나는 내일, 어제의 너와 만난다', '키싱부스', '건축학 개론', '너와 100번째 사랑', '말 할 수 없는 비밀', '피끓는 청춘',
         '눈물이 주룩주룩',
         '울고싶은 나는 고양이 가면을 쓴다', '8월의 크리스마스', '조제, 호랑이 그리고 물고기들', '지금, 만나러 갑니다', '이클립스', '어거스트 러쉬', '악마는 프라다를 입는다',
         '엣지 오브 투모로', '컨테이젼',
         '가타카', '올드 가드', '캐스트 어웨이', '미스 페레그린과 이상한 아이들의 집', '로맨틱 홀리데이', '패밀리 맨', '에린 브로코비치', '월드워Z', '데드풀', '메멘토',
         '완벽한 타인',
         '극한직업', '곤지암', '변신', '협상']

# cnt = 5271
#
# base_url = "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query="
#
# for m in movie:
#     title = m
#     data = requests.get(base_url + urllib.parse.quote(title), headers=headers)
#     soup = BeautifulSoup(data.text, 'html.parser')
#
#     try:
#         code = soup.select_one("#main_pack > div.sc_new.cs_common_module.case_empasis.color_15._au_movie_content_wrap > div.cm_top_wrap._sticky > div.title_area._title_area > h2 > a")["href"].split("=")[1]
#         movie_url = "https://movie.naver.com/movie/bi/mi/basic.nhn?code="
#         info = requests.get(movie_url + code, headers=headers)
#         ssoup = BeautifulSoup(info.text, 'html.parser')
#
#         try:
#             thumbnail = soup.select_one("#main_pack > div.sc_new.cs_common_module.case_empasis.color_4._au_movie_content_wrap > div.cm_content_wrap > div.cm_content_area._cm_content_area_info > div.cm_info_box > div.detail_info > a > img")["src"]
#         except:
#             thumbnail = "None"
#             pass
#
#         try:
#             country = soup.select_one("#main_pack > div.sc_new.cs_common_module.case_empasis.color_4._au_movie_content_wrap > div.cm_content_wrap > div.cm_content_area._cm_content_area_info > div.cm_info_box > div.detail_info > dl > div:nth-child(1) > dd").text()
#         except:
#             country = "None"
#             pass
#
#         try:
#             genre = soup.select_one(
#                 "#main_pack > div.sc_new.cs_common_module.case_empasis.color_4._au_movie_content_wrap > div.cm_content_wrap > div.cm_content_area._cm_content_area_info > div.cm_info_box > div.detail_info > dl > div:nth-child(1) > dd").text
#
#         except:
#             genre = "None"
#             pass
#
#         try:
#             runtime = soup.select_one(
#                 "#main_pack > div.sc_new.cs_common_module.case_empasis.color_4._au_movie_content_wrap > div.cm_content_wrap > div.cm_content_area._cm_content_area_info > div.cm_info_box > div.detail_info > dl > div:nth-child(1) > dd").text
#         except:
#             runtime = "None"
#             pass
#
#         try:
#             director = soup.select_one(
#                 "#content > div.article > div.mv_info_area > div.mv_info > dl > dd:nth-child(4) > p > a").text
#         except:
#             director = "None"
#             pass
#
#         try:
#             cast_list = soup.select_one("#content > div.article > div.mv_info_area > div.mv_info > dl > dd:nth-child(6) > p a")
#             temp=[]
#             for c in cast_list:
#                 temp.append(c.select_one("div > div > strong > a").text)
#             cast = ', '.join(temp[1:])
#
#
#         except:
#             cast = "None"
#             pass
#
#         try:
#             desc = ssoup.select_one(
#                 "#content > div.article > div.section_group.section_group_frst > div:nth-child(1) > div > div.story_area > p").text.strip()
#         except:
#             desc = "None"
#             pass
#
#         try:
#             year = soup.select_one("#main_pack > div.sc_new.cs_common_module.case_empasis.color_15._au_movie_content_wrap > div.cm_top_wrap._sticky > div.title_area._title_area > div > span:nth-child(5)").text
#         except:
#             year = "None"
#             pass
#
#     except:
#         country = "None"
#         genre = "None"
#         runtime = "None"
#         director = "None"
#         cast = "None"
#         desc = "None"
#         thumbnail = "None"
#         year = "None"
#
#     finally:
#         doc = {
#             'title': title,
#             'type': '영화',
#             'country': country,
#             'genre': genre,
#             'runtime': runtime,
#             'director': director,
#             'cast': cast,
#             'desc': desc,
#             'thumbnail': thumbnail,
#             'contentId': cnt,
#             'year':year
#         }
#
#     print(doc)
#     cnt += 1

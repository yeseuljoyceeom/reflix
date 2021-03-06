Reflix
=======
넷플릭스의 모든 것! 리뷰작성부터, 최신 & 곧 종료되는 작품 정보까지~ 자유게시판에서 유저들과 영화추천 및 자유로운 소통도 가능한 웹사이트.  
For visiting Reflix, click [here](http://reflix.shop/)  
For a video demo, click [here](https://youtu.be/nuldX9TPSHU) 

### 프로젝트 소개
    프로그래밍 공부를 하면서 만들어 본 개인 프로젝트용 넷플릭스 컨텐츠 리뷰사이트입니다. 
    검색필터를 이용해 원하는 컨텐츠를 찾아볼 수 있으며 평점 및 댓글도 남길 수 있습니다. 
    또한, 자유게시판에서는 유저들과 자유로운 소통도 가능합니다. 

### 개발환경
    운영 체제: MAC OS
    IDE: PyCharm 2020.3
    Front-end: jQuery 3.5.1, CSS, bootstrap 4.0.0, Jinja template
    Back-end: Flask1.1.2
    Database: MongoDB 4.4.3 (MongoDB GUI: Robo 3T 1.4.2)
    Cloud server: AWS EC2 (FTP: FileZilla)
    

### 프로젝트 기능
1. 로그인/회원가입
          
        - 토큰기반 인증방식 활용 (JWT)   
        - 회원가입시 유저정보를 DB에 저장 (비밀번호는 단방향으로 암호화해서 저장)
        - 로그인시 유저정보 확인후 JWT토큰을 만들어 사용자 쿠키에 저장 (1시간짜리 토큰)
        - 로그인 인증이 필요한 요청마다 사용자 쿠키에서 토큰을 가져와 사용자를 검증

2. 컨텐츠 검색

        - 사용자가 키워드를 입력하면 요청 헤더로 보내 DB에서 찾은 후 해당되는 컨텐츠들을 표시  
        - 페이징 처리를 통해 한번에 최대 25개 컨텐츠 표시

3. 검색옵션
    
        - 정렬옵션: 최신순, 오래된순, 평점순
        - 필터옵션: 영화, 드라마, 예능, 다큐멘터리, 애니메이션
        - 정렬옵션, 필터옵션과 검색기능 중복사용가능

4. 컨텐츠 별점&댓글,좋아요

        - 사용자가 표시한 별점과 작성한 댓글을 댓글 고유번호와 사용자 정보와 함께 DB에 저장
        - 사용자가 댓글에 좋아요를 누를시 댓글 고유번호를 통해 좋아요 개수 업데이트
        - 댓글은 좋아요순으로 정렬

5. 자유게시판
  
        - Create: 게시글작성
        - Read: 게시글 열람
        - Update: 게시글 수정
        - Delete: 게시글 삭제
        - 토큰을 통해 사용자 검증후 게시글 글쓴이 본인에게만 수정 및 삭제 권한 부여
        - 게시글에 댓글 작성 가능

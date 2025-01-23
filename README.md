# YBIGTA_newbie_team_project

## 팀소개
안녕하세요! 6조입니다!!! 화이팅화이팅~~

## 팀원 소개

| **손재훈(조장)**          | **김이지**                   | **신소연**              |
|:-------------------------:|:---------------------------:|:-----------------------:|
| 00년생 응용통계학과 21학번 | 01년생 컴퓨터과학과 20학번 | |
| 반갑습니다! 잘 부탁드립니다~ | 잘 부탁드립니다! |  |


## 사진

#### branch_protection.png
![branch_protection.png](github/branch_protection.png)

#### push_rejected.png
![push_rejected.png](github/push_rejected.png)

#### merged_손재훈.png
![merged_손재훈.png](github/merged_손재훈.png)

#### merged_김이지.png
![merged_김이지.png](github/merged_김이지.png)

#### merged_신소연.png
![merged_신소연.png](github/merged_신소연.png)

## app 프로젝트 실행 방법

1. 가장 상위 폴더 디렉토리로 이동
2. 필요한 라이브러리 설치 : pip install -r requirements.txt 
3. 실행 : uvicorn app.main:app --reload
4. 웹 브라우저를 켜서 : http://127.0.0.1:8000/static/index.html
5. 기능 살펴보기


## crawling 데이터 정보

#### 영화 : 기생충
1. 네이버 영화 리뷰(국내)
  - 크롤링한 사이트의 링크 : "https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&ssc=tab.nx.all&query=%EC%98%81%ED%99%94+%EA%B8%B0%EC%83%9D%EC%B6%A9+%EA%B4%80%EB%9E%8C%ED%8F%89&oquery=%EC%98%81%ED%99%94+%EA%B8%B0%EC%83%9D%EC%B6%A9+%EA%B4%80%EB%9E%8C%ED%8F%89%27&tqi=iH4Yfdqo1e8sseUNrBRssssss0Z-072431"
  - 데이터 형식 : review_type(str), sort_type(str), writing_date(str), star_rating(str), comment(str), upvote(int), downvote(int) 의 컬럼으로 구성됨
  - 개수 : 1092개

2. IMDB 영화 리뷰(해외)
  - 크롤링한 사이트의 링크 : "https://www.imdb.com/title/tt6751668/reviews/?ref_=tt_ururv_sm&spoilers=EXCLUDE&sort=user_rating%2Cdesc"
  - 데이터 형식 : star_rating(int),title(str),content(str),date(str)의 컬럼으로 구성됨
  - 개수 : 2977개


## crawling code 실행 방법
1. 터미널 위치를 crawling 폴더로 이동
2. python main.py -o ../../database --all



## EDA
1. 네이버 영화 리뷰
2. IMDB 영화 리뷰

![IMDB_자주등장단어_긍정리뷰.png](review_analysis/plots/IMDb 리뷰 자주 등장하는 단어 - 긍정적 리뷰.png)
![IMDB_자주등장단어_부정리뷰.png](review_analysis/plots/IMDb 리뷰 자주 등장하는 단어 - 긍정적 리뷰.png)
![IMDB_자주등장단어_전체리뷰.png](review_analysis/plots/IMDb 리뷰 자주 등장하는 단어 - 전체 리뷰.png)

## preprocessing code 실행 방법
1. 터미널 위치를 crawling 폴더로 이동
2. python main.py -o ../../database --all


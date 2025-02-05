from pymongo import MongoClient
import os

# .env 파일에서 환경변수 로드
mongo_url = os.getenv("MONGODB_URI")
mongo_client = MongoClient(mongo_url)

# 'movie_review_db' 데이터베이스 확인
mongo_db = mongo_client["movie_review_db"]

# 현재 데이터베이스 내 컬렉션 목록 출력
collections = mongo_db.list_collection_names()
print(f"✅ 현재 데이터베이스에 존재하는 컬렉션: {collections}")

# 만약 컬렉션이 존재하면, 5개만 샘플 조회
if "raw_reviews" in collections:
    sample_docs = list(mongo_db["raw_reviews"].find().limit(5))
    print(f"✅ `raw_reviews` 샘플 데이터: {sample_docs}")
else:
    print("❌ `raw_reviews` 컬렉션이 존재하지 않습니다.")

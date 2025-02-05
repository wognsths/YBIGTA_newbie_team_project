from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

mongo_url = os.getenv("MONGODB_URI")
mongo_client = MongoClient(mongo_url)

mongo_db = mongo_client["movie_review_db"]

print(mongo_db.list_collection_names())

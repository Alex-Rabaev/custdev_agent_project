from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_database("business_buddy")

# Коллекция пользователей
users_collection = db.get_collection("users")
from pymongo import MongoClient
from django.conf import settings

def get_mongo_client():
    return MongoClient(settings.MONGO_DB_URI)

def get_database(db_name):
    client = get_mongo_client()
    return client[db_name]

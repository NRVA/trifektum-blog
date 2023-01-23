import pymongo
import os
from pymongo.server_api import ServerApi

MONGODB_SERVER = os.environ['MONGODB_SERVER']
MONGO_DB = "myStockScreener"
MONGO_DIVIDEND_COLLECTION = "DividendScreener"

class MongoDBPipeline():
    def __init__(self):
        connection = pymongo.MongoClient(
            MONGODB_SERVER,
            server_api=ServerApi('1')
        )
        db = connection.get_database(MONGO_DB)
        self.collection = db[MONGO_DIVIDEND_COLLECTION]

    def process_item(self, item):
        self.collection.insert_one(item)


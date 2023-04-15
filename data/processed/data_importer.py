import pymongo
import dotenv
import os
import json
import time
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='data_logger.log', filemode='w')
data_logger = logging.getLogger("data_logger")

class DataImporter:

    def __init__(self, db_name = 'Goodreads', collection_name = 'Books'):
        self.db_name = db_name
        self.collection_name = collection_name
        self.collection = None
        self.db = None
        self.client = None
        self.mongo_uri = None
        self.username = None
        self.password = None
        self.amount = 0
        self.pipeline = [{'$set': {'genres': {'$objectToArray': '$genres'},'awards': {'$objectToArray': '$awards'},'primary_lists': {'$objectToArray':'$primary_lists'}}},  {'$project': {'_id': 0}},  {'$limit': self.amount}]
        self.boot_connection()

    def boot_connection(self):
        self.set_user()
        self.mongo_uri = f"mongodb+srv://{self.username}:{self.password}@recosystems.hyjorhd.mongodb.net/?retryWrites=true&w=majority"
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.db_name]
        self.collection = self.client[self.db_name][self.collection_name]
        data_logger.debug(f"MongoDB connection established: {self.client}")
        data_logger.debug(f"MongoDB database: {self.db}")
        data_logger.debug(f"MongoDB collection: {self.collection}")
        

    def set_user(self):
        if os.environ.get('MongoDBpassword') and os.environ.get('MongoDBuser'):
            del os.environ["MongoDBpassword"]
            del os.environ["MongoDBuser"]
        dotenv.load_dotenv()
        self.password = os.getenv('MongoDBpassword')
        self.username = os.getenv('MongoDBuser')
        data_logger.debug(f"MongoDB username: {self.username}")
        data_logger.debug(f"MongoDB password: {self.password}")

    def import_data(self, write = False, amount = 1):
        self.set_db_collection()
        self.amount = amount
        data = self.collection.aggregate(self.pipeline)
        data = [doc for doc in data]
        if write:
            # Write data to file with name data_db_collection_date.json
            with open(f'data_{(self.db_name).lower()}_{(self.collection_name).lower()}_{time.strftime("%Y%m%d")}.json', 'w') as outputfile:
                json.dump((data), outputfile)
            return data
        else:
            return data
      
    def log_all(self):
        data_logger.debug(f"MongoDB client: {self.client}")
        data_logger.debug(f"MongoDB database: {self.db}")
        data_logger.debug(f"MongoDB collection: {self.collection}")
        data_logger.debug(f"MongoDB URI: {self.mongo_uri}")

    def set_db_collection(self, db_name = '', collection_name = ''):
        if db_name != '':
            self.db_name = db_name
            self.db = self.client[self.db_name]
        if collection_name != '':
            self.collection_name = collection_name
            self.collection = self.client[self.db_name][self.collection_name]

    def write_data(self, data):
        with open(f'data_{time.strftime("%Y%m%d")}.json', 'w') as outputfile:
            json.dump((data), outputfile)


# What to imporve: 
# - Make pypackage out of this


        
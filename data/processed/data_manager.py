import pymongo
import dotenv
import os
import json
import time
import logging
import pandas as pd
from pymongo import UpdateOne

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='data_logger.log', filemode='w')
data_logger = logging.getLogger("data_logger")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
data_logger.addHandler(console_handler)

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
        self.pipeline = [{'$set': {'genres': {'$objectToArray': '$genres'},'awards': {'$objectToArray': '$awards'},'primary_lists': {'$objectToArray':'$primary_lists'}}},  {'$project': {'_id': 0}}]
        self.boot_connection()

    def boot_connection(self):
        self.set_user()
        self.mongo_uri = f"mongodb+srv://{self.username}:{self.password}@recosystems.hyjorhd.mongodb.net/?retryWrites=true&w=majority"
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.db_name]
        self.collection = self.client[self.db_name][self.collection_name]
        data_logger.debug(f"MongoDB database: {self.db_name}")
        data_logger.debug(f"MongoDB collection: {self.collection_name}")
        

    def set_user(self):
        if os.environ.get('MongoDBpassword') and os.environ.get('MongoDBuser'):
            del os.environ["MongoDBpassword"]
            del os.environ["MongoDBuser"]
        dotenv.load_dotenv()
        self.password = os.getenv('MongoDBpassword')
        self.username = os.getenv('MongoDBuser')

    def import_data(self, write = False, use_pipeline = False):
        self.set_db_collection()
        if use_pipeline and self.pipeline != None:
            data = self.collection.aggregate(self.pipeline)
        elif use_pipeline and self.pipeline == None:
            data_logger.debug("No pipeline set, using find()")
            data_logger.debug("Use method set_pipeline(pipeline) to set pipeline")
            data = self.collection.find()
        else:
            data = self.collection.find()
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

    def set_pipeline(self, pipeline):
        self.pipeline = pipeline
    
    



class DataExporter:
    
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

        def export_data(self, data):
            try:
                bulk_operations = []
                for processed_document in data:
                    book_id = processed_document['book_id']
                    filter = {'book_id': book_id}
                    update_operation = UpdateOne(filter, {'$set': processed_document}, upsert=True)
                    bulk_operations.append(update_operation)
                result = self.collection.bulk_write(bulk_operations)
                data_logger.debug(f"Inserted/updated {result.upserted_count} documents")
                data_logger.debug(f"Data exported to MongoDB")
                data_logger.debug(f"MongoDB client: {self.client}")
                data_logger.debug(f"MongoDB database: {self.db}")
                data_logger.debug(f"MongoDB collection: {self.collection}")

            except Exception as e:
                data_logger.error(f"Error exporting data to MongoDB: {e}")

        def format_csv_to_json(self, file_name):
            df = pd.read_csv(file_name)
            # Convert the Pandas dataframe to a list of dictionaries
            data = df.to_dict(orient='records')
            return data
        
                
        
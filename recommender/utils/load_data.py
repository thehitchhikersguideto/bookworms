""" LOAD DATA """


import os
import json
import time
from data_manager import DataManager
from dotenv import load_dotenv
import pymongo
import pandas as pd


# Load environment variables
load_dotenv()


def load_data_for_xgboost(book_names):
    """Load data from MongoDB"""
    # Setting the environment variables: 
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_DB = os.getenv('MONGO_DB')
    MONGO_COLLECTION = os.getenv('MONGO_COLLECTION')
    # DB 
    # COLLLECTION
    
    pipeline = [
    {
        '$match': {
            'book_id': {
                '$in': [
                    '77203.The_Kite_Runner', '929.Memoirs_of_a_Geisha'
                ]
            }
        }
    }, {
        '$project': {
            'all_lists_link': 0, 
            'date_time_of_scrape': 0, 
            'isbn': 0, 
            '_id': 0
        }
    }, {
        '$set': {
            'genres': {
                '$objectToArray': '$genres'
            }, 
            'awards': {
                '$objectToArray': '$awards'
            }, 
            'primary_lists': {
                '$objectToArray': '$primary_lists'
            }
        }
    }

    ]

    # Connect to Mongo 
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    ret_raw = collection.aggregate(pipeline)
    ret = pd.DataFrame(ret_raw)
    return ret

def load_data_for_cosine_sim():
    pass
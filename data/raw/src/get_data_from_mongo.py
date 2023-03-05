
# imports
import os
import sys
import pandas as pd
from config import get_mongo_config
import pymongo
from typing import Collection, Tensor
import tensorflow as tf
import logging as log

# We need to have several data pull and push functions to allow flexibility with the EDA as well as working with the ML models


# first we create a connection

def define_connection(mongo_config: dict):
    # define the connection
    client = pymongo.MongoClient(mongo_config.mongo_uri)
    db = client[mongo_config.mongo_db]
    col = db[mongo_config.mongo_col]
    return col     


def data_from_scraper_gen():
    # get the data from the scraper
    for file in get_book_reviews():
        yield file

def data_to_mongo_gen(col: Collection):
    # push the data to mongo
    for file in data_from_scraper_gen():
        col.insert_one(file)
        yield file
    
def run_pipeline():
    # use pipe notation
    mongo_config = get_mongo_config()
    col = define_connection(mongo_config)
    for data in data_to_mongo_gen(col):
        log.info(f'Pushed {data} to the {col} collection.')
        
    
if __name__ == '__main__':
    run_pipeline()






""" LOAD DATA """
import os
import json
import time
import data_manager
from dotenv import load_dotenv
import pymongo
import pandas as pd


# Load environment variables
load_dotenv()


def load_data_for_xgboost(book_names):
    """Load data from MongoDB"""
    pipeline = [
    {
        '$match': {
            'book_id': {
                '$in': book_names # array
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
    data_importer_xgboost = data_manager.DataImporter(db_name='Goodreads', collection_name='Books')
    data_importer_xgboost.set_pipeline(pipeline)
    ret = data_importer_xgboost.import_data(use_pipeline=True)

    # Connect to Mongo 
    """client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION] """
    return ret

def load_data_for_cosine_sim():
    data_importer_cosine = data_manager.DataImporter(db_name='Processed_Data', collection_name='Embeddings')
    # Get the embeddings from the database
    data_importer_cosine.set_pipeline([
        {'$project': {'_id': 0}}
    ])
    embed_data = data_importer_cosine.import_data(use_pipeline=True)
    df_embeddings = pd.DataFrame(embed_data)
    available_books = df_embeddings['book_id'].tolist()

    # Get the books from the database
    data_importer_cosine.set_db_collection(db_name='Processed_Data', collection_name='processed_books')
    # Only grab the books we have embeddings for and dont grab any columns we dont need
    data_importer_cosine.set_pipeline(pipeline = [{"$match": {"book_id": {"$in": available_books}}},{"$project": {"_id": 0,"series": 0,"price": 0,"language": 0,"primary_lists": 0,"year_published": 0, 'description': 0, 'rating':0}}])
    book_data = data_importer_cosine.import_data(use_pipeline=True)
    df_books = pd.DataFrame(book_data)
    titles_and_ids = df_books[['book_id', 'title']]
    df_books.drop(columns=['title'], inplace=True)
    print("Data imported, preprocessing...")
    # Merge the two dataframes based on the book_id
    df_books_and_embeddings = pd.merge(df_books, df_embeddings, on='book_id')

    return df_books_and_embeddings, titles_and_ids
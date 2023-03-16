import pymongo
import pandas as pd
from dotenv import load_dotenv
import os
import logging

# Logging Params
# Refreshes the log file with each run, delete filemode='w' to append
logging.basicConfig(filename='mongoDBHandler.log', filemode='w', level=logging.DEBUG)


def load_env_vars():
    # Load MongoDB credentials from .env file
    if os.environ.get('password') and os.environ.get('user'):
        del os.environ["password"]
        del os.environ["user"]
    
    load_dotenv()
    password = os.environ.get('password')
    user = os.environ.get('user')
    logging.info("Loaded MongoDB credentials from .env file")
    return password, user

def load_mongo(password,user):
    SOURCE_DB = 'Goodreads'
    SOURCE_COLLECTION = 'Books'
    SOURCE_COLLECTION_REVIEWS = 'BookReviews'
    SOURCE_COLLECTION_BOOKLIST = 'BookList'
    MONGO_URI = f"mongodb+srv://{user}:{password}@recosystems.hyjorhd.mongodb.net/?retryWrites=true&w=majority"
    logging.info("Initializing MongoDB connection")
    logging.info("MongoDB URI: " + MONGO_URI)
    logging.info("MongoDB Database: " + SOURCE_DB)
    logging.info("User: " + user)
    client = pymongo.MongoClient(MONGO_URI)
    db = client[SOURCE_DB]
    collection_books = db[SOURCE_COLLECTION]
    collection_book_reviews = db[SOURCE_COLLECTION_REVIEWS]
    collection_book_list = db[SOURCE_COLLECTION_BOOKLIST]
    collections = [collection_books, collection_book_reviews, collection_book_list]
    logging.info("MongoDB connection initialized, collections loaded")
    return collections

# MongoDB requires special characters to be encoded in the URI (% + ASCII code)

def start_mongo():
    password, user = load_env_vars()
    collections = load_mongo(password,user)
    return collections

def insert_into_mongo(collection, jsonResult):
    try:
        collection.insert_many(jsonResult)
        for i in range(len(jsonResult)):
            logging.info("Inserted " + jsonResult[i]['Title'] + " into " + str(collection))
        return True
    except Exception as e:
        logging.error("Failed to insert " + jsonResult[i]['Title'] + " into " + str(collection))
        logging.error(e)
        return False
    


# ALL METHODS RELATED TO THE SCRAPED STATUS OF BOOKS, WORKS IN CONJUCTION WITH THE BOOKLIST COLLECTION IN MONGODB
# Function to check if the href exists in the collection 
def href_exists(collection, href):
    if collection.find_one(href):
        return True
    else:
        return False

# Function to init the href with a scraped value of 0 indicating that it has not been scraped yet
def href_init(href):
    href = {"href": href, "scraped": 0}
    return href
    
# Function to insert the href into the collection, if it does not already exist
def insert_href_into_book_list(collection, href):
    try:
        if href_exists(collection, href):
            return False
        else:
            # Here href changes from a string to a dictionary and is inited with a scraped value of 0 indicating that it has not been scraped yet
            href_with_scrape_signature = href_init(href)
            collection.insert_one(href_with_scrape_signature)
            logging.info("Inserted " + href + " into " + str(collection))
            return True
    except Exception as e:
        logging.error("Failed to insert " + href + " into " + str(collection))
        logging.error(e)
        return False
    
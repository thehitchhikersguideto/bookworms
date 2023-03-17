import pymongo
import pandas as pd
from dotenv import load_dotenv
import os
import logging

# Logging Params
# Refreshes the log file with each run, delete filemode='w' to append
logging.basicConfig(filename='mongoDBHandler.log', filemode='w', level=logging.DEBUG)


class MongoReco:

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def load_env_vars(self):
        # Load MongoDB credentials from .env file
        if os.environ.get('password') and os.environ.get('user'):
            del os.environ["password"]
            del os.environ["user"]
        
        load_dotenv()
        password = os.environ.get('password')
        user = os.environ.get('user')
        logging.info("Loaded MongoDB credentials from .env file")
        return password, user

    def load_mongo(self,password,user):
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
    @classmethod
    def start_mongo(cls):
        password, user = cls.load_env_vars()
        collections = cls.load_mongo(password,user)
        return collections
        
    collections = start_mongo()
    collection_book = collections[0]
    collection_book_reviews = collections[1]
    collection_book_list = collections[2]

    # ALL METHODS RELATED TO THE SCRAPED STATUS OF BOOKS, WORKS IN CONJUCTION WITH THE BOOKLIST COLLECTION IN MONGODB
    # Function to check if the href exists in the collection 
    def href_exists(collection, href):
        if collection.find_one({"href": href}):
            return True
        else:
            return False

    # Function to init the href with a scraped value of 0 indicating that it has not been scraped yet
    def href_init(href):
        href = {"href": href, "scraped": 0}
        return href
        

    # Function to insert the href into the collection, if it does not already exist
    @classmethod
    def insert_href_into_book_list(cls, href, many=False):
        try:
                if many:
                    hrefs_with_scrape_signature = []
                    for href in href:
                        if not cls.href_exists(cls.collection_book_list, href):
                             href_with_scrape_signature = cls.href_init(href)
                             hrefs_with_scrape_signature.append(href_with_scrape_signature)
                        else:
                            logging.info("href " + href + " already exists in " + str(cls.collection_book_list))
                            logging.info("continuing to next href")
                            continue
                    cls.collection_book_list.insert_many(hrefs_with_scrape_signature)
                    logging.info("Inserted " + str(len(hrefs_with_scrape_signature)) + " hrefs into " + str(cls.collection_book_list))
                else:
                    # Here href changes from a string to a dictionary and is inited with a scraped value of 0 indicating that it has not been scraped yet
                    href_with_scrape_signature = cls.href_init(href)
                    cls.collection_book_list.insert_one(href_with_scrape_signature)
                    logging.info("Inserted " + href + " into " + str(cls.collection_book_list))
                    return True
        except Exception as e:
                logging.error("Failed to insert " + href + " into " + str(cls.collection_book_list))
                logging.error(e)
                return False
    @classmethod
    def insert_into_books(cls, jsonResult, many=False):
        try:
            if many:
                cls.collection_books.insert_many(jsonResult)
                for i in range(len(jsonResult)):
                    logging.info("Inserted " + jsonResult[i]['Title'] + " into " + str(cls.collection_books))
                return True
            else:
                cls.collection_books.insert_one(jsonResult)
                logging.info("Inserted " + jsonResult['Title'] + " into " + str(cls.collection_books))
                return True
        except Exception as e:
            for i in range(len(jsonResult)):
                logging.error("Failed to insert " + jsonResult[i]['Title'] + " into " + str(cls.collection_books))
            logging.error(e)
            return False
    
    # Reviews are inserted into the BookReviews collection
    @classmethod
    def insert_into_book_reviews(cls, jsonResult, many=False):
        try:
            if many:
                cls.collection_book_reviews.insert_many(jsonResult)
                for i in range(len(jsonResult)):
                    logging.info("Inserted " + jsonResult[i]['Title'] + " into " + str(cls.collection_book_reviews))
                return True
            else:
                cls.collection_book_reviews.insert_one(jsonResult)
                logging.info("Inserted " + jsonResult['Title'] + " into " + str(cls.collection_book_reviews))
                return True
        except Exception as e:
            logging.error("Failed to insert " + jsonResult[i]['Title'] + " into " + str(cls.collection_book_reviews))
            logging.error(e)
            return False
        
    @classmethod
    def retrieve_books_from_book_lists(cls, amount):
        try: 
            hrefs = []
            # only retrive books whose scraped value is 0
            for book in cls.collection_book_list.find({"scraped": 0}):
                hrefs.append(book['href'])
            return hrefs[:amount]
        except Exception as e:
            logging.error("Failed to retrieve books from " + str(cls.collection_book_list))
            logging.error(e)
            return False
    

    # The update function works under the idea that some books may not succeed in being scraped thus this function will take in a list of hrefs and update the scraped value to 1
    @classmethod
    def update_book_list(cls,hrefs):
        try:
            for href in hrefs:
                cls.collection_book_list.find({"href": href})[0]['scraped'] = 1
            logging.info("Updated " + str(len(hrefs)) + " hrefs in " + str(cls.collection_book_list))
            return True
        except Exception as e:
            logging.error("Failed to update " + str(len(hrefs)) + " hrefs in " + str(cls.collection_book_list))
            logging.error(e)
            return False
        
    # For the reviews we need to retrieve the review hrefs from the books collection
    @classmethod
    def retrieve_review_hrefs_from_books(cls, amount):
        try:
            r_hrefs = []
            for book in cls.collection_books.find():
                r_hrefs.append(book['Review_Href'])
            return r_hrefs[:amount]
        except Exception as e:
            logging.error("Failed to retrieve review hrefs from " + str(cls.collection_books))
            logging.error(e)
            return False
    
        

        
    

         
    
        
    
        
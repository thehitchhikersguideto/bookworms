import pymongo
from dotenv import load_dotenv
import os
import logging

# Logging Params
# Refreshes the log file with each run, delete filemode='w' to append
logging.basicConfig(filename='mongoDBHandler.log', filemode='w', level=logging.DEBUG)


class MongoReco:

    __instance = None
    __collection_books = None
    __collection_book_reviews = None
    __collection_book_list = None

    def __new__(cls):
        if cls.__instance is None:
            logging.info("Initializing MongoReco")
            cls.__instance = object.__new__(cls)
            cls.start_mongo(cls)
        return cls.__instance
    

    def load_env_vars(self):
        # Load MongoDB credentials from .env file
        if os.environ.get('MongoDBpassword') and os.environ.get('MongoDBuser'):
            del os.environ["MongoDBpassword"]
            del os.environ["MongoDBuser"]
        
        load_dotenv()
        password = os.environ.get('MongoDBpassword')
        user = os.environ.get('MongoDBuser')
        logging.info("Loaded MongoDB credentials from .env file")
        return password, user

    def load_mongo(self,password,user):
        SOURCE_DB = 'Goodreads'
        SOURCE_COLLECTION = 'Books'
        SOURCE_COLLECTION_REVIEWS = 'BookReviews'
        SOURCE_COLLECTION_BOOKLIST = 'BookList'
        MONGO_URI = f"mongodb+srv://{user}:{password}@recosystems.hyjorhd.mongodb.net/?retryWrites=true&w=majority"
        logging.info("Initializing MongoDB connection")
        # logging.info("MongoDB URI: " + MONGO_URI)
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
    # @classmethod
    def start_mongo(self):
        password, user = self.load_env_vars(self)
        collections = self.load_mongo(self,password,user)
        self.__collection_books = collections[0]
        self.__collection_book_reviews = collections[1]
        self.__collection_book_list = collections[2]
        logging.info("MongoDB connection initialized, collections loaded")
        logging.info("Collection_books: " + str(self.__collection_books))
        logging.info("Collection_book_reviews: " + str(self.__collection_book_reviews))
        logging.info("Collection_book_list: " + str(self.__collection_book_list))
        

    # ALL METHODS RELATED TO THE SCRAPED STATUS OF BOOKS, WORKS IN CONJUCTION WITH THE BOOKLIST COLLECTION IN MONGODB
    # Function to check if the href exists in the collection 
    def href_exists(collection, href):
        logging.info("Checking if href " + href + " exists in " + str(collection))
        if collection.find_one({"href": href}):
            return True
        else:
            return False

    # Function to init the href with a scraped value of 0 indicating that it has not been scraped yet
    def href_init(href):
        book_id = href.split('/')[-1]
        href = {"href" : href, "book_id" : book_id ,"scraped" : 0, "review_scraped" : 0}
        return href
        

    # Function to insert the href into the collection, if it does not already exist
    @classmethod
    def insert_href_into_book_list(cls, href, many=False):
        try:
                if many:
                    hrefs_with_scrape_signature = []
                    for href in href:
                        logging.info("Checking if href " + href + " exists in " + str(cls.__collection_book_list) + " of type " + str(type(cls.__collection_book_list)))
                        if not cls.href_exists(cls.__collection_book_list, href):
                             href_with_scrape_signature = cls.href_init(href)
                             hrefs_with_scrape_signature.append(href_with_scrape_signature)
                        else:
                            logging.info("href " + href + " already exists in " + str(cls.__collection_book_list))
                            logging.info("continuing to next href")
                            continue
                    cls.__collection_book_list.insert_many(hrefs_with_scrape_signature)
                    logging.info("Inserted " + str(len(hrefs_with_scrape_signature)) + " hrefs into " + str(cls.__collection_book_list))
                else:
                    # Here href changes from a string to a dictionary and is inited with a scraped value of 0 indicating that it has not been scraped yet
                    href_with_scrape_signature = cls.href_init(href)
                    cls.__collection_book_list.insert_one(href_with_scrape_signature)
                    logging.info("Inserted " + href + " into " + str(cls.__collection_book_list))
                    return True
        except Exception as e:
                logging.error("Failed to insert " + href + " into " + str(cls.__collection_book_list))
                # logging.info(e)
                return False
        
    @classmethod
    def insert_into_books(cls, dict_result, many=False):
        try:
            if many:
                cls.__collection_books.insert_many(dict_result)
                for i in range(len(dict_result)):
                    logging.info("Inserted " + dict_result[i]['title'] + " into " + str(cls.__collection_books))
                return True
            else:
                cls.__collection_books.insert_one(dict_result)
                logging.info("Inserted " + dict_result['title'] + " into " + str(cls.__collection_books))
                return True
        except Exception as e:
            if many:
                for i in range(len(dict_result)):
                    logging.info("Failed to insert " + dict_result[i]['title'] + " into " + str(cls.__collection_books))
            else:
                logging.info("Failed to insert " + dict_result['title'] + " into " + str(cls.__collection_books))
            # logging.info(e)
            return False
        
    # Used to update the review_scraped value to 0 if the book was accidently changed to 1, takes a list of hrefs or leave it blank to reset all
    @classmethod
    def reset_scraped_reviews(cls, hrefs = None):
        if hrefs:
            try: 
                for href in hrefs:
                    cls.__collection_book_list.update_one({"href": href}, {"$set": {"review_scraped": 0}})
                    logging.info("Reset scraped to 0 for " + href + " in " + str(cls.__collection_book_list))
                return True
            except Exception as e:
                logging.error("Failed to reset scraped to 0 for " + href + " in " + str(cls.__collection_book_list))
                # logging.info(e)
                return False
            
        else:
            try:
                cls.__collection_book_list.update_many({}, {"$set": {"review_scraped": 0}})
                logging.info("Reset review_scraped to 0 for all hrefs in " + str(cls.__collection_book_list))
                return True
            except Exception as e:
                logging.error("Failed to reset review_scraped to 0 for all hrefs in " + str(cls.__collection_book_list))
                # logging.info(e)
                return False
    
    # Used in case something gets misaligned and the scraped status of a book is not updated it can be done manually, input should be a list of hrefs
    @classmethod
    def reset_scraped_books(cls, hrefs = None):
        if hrefs:
            try: 
                for href in hrefs:
                    cls.__collection_book_list.update_one({"href": href}, {"$set": {"scraped": 0}})
                    logging.info("Reset scraped to 0 for " + href + " in " + str(cls.__collection_book_list))
                return True
            except Exception as e:
                logging.error("Failed to reset scraped to 0 for " + href + " in " + str(cls.__collection_book_list))
                # logging.info(e)
                return False

        else:
            try:
                cls.__collection_book_list.update_many({}, {"$set": {"scraped": 0}})
                logging.info("Reset scraped to 0 for all hrefs in " + str(cls.__collection_book_list))
                return True
            except Exception as e:
                logging.error("Failed to reset scraped to 0 for all hrefs in " + str(cls.__collection_book_list))
                # logging.info(e)
                return False


    
    # Reviews are inserted into the BookReviews collection
    @classmethod
    def insert_into_book_reviews(cls, dict_result, many=False):
        try:
            if many:
                cls.__collection_book_reviews.insert_many(dict_result)
                for i in range(len(dict_result)):
                    logging.info("Inserted " + dict_result[i]['Title'] + " into " + str(cls.__collection_book_reviews))
                return True
            else:
                cls.__collection_book_reviews.insert_one(dict_result)
                logging.info("Inserted " + dict_result['Title'] + " into " + str(cls.__collection_book_reviews))
                return True
        except Exception as e:
            logging.error("Failed to insert " + dict_result[i]['Title'] + " into " + str(cls.__collection_book_reviews))
            # logging.info(e)
            return False
        
    @classmethod
    def retrieve_books_from_book_lists(cls, amount):
        try: 
            hrefs = []
            # only retrive books whose scraped value is 0
            books = cls.__collection_book_list.find({"scraped": 0}).limit(amount)
            for book in books:
                hrefs.append(book['href'])
            return hrefs
        except Exception as e:
            logging.error("Failed to retrieve books from " + str(cls.__collection_book_list))
            # logging.info(e)
            return False
    

    # The update function works under the idea that some books may not succeed in being scraped thus this function will take in a list of hrefs and update the scraped value to 1
    @classmethod
    def update_book_list_book_scraped(cls,book_ids):
        try:
            for book_id in book_ids:
                logging.info("Updating " + str(book_id) + " in " + str(cls.__collection_book_list))
                cls.__collection_book_list.update_one({"book_id": str(book_id)}, {"$set": {"scraped": 1}})
            logging.info("Updated " + str(len(book_ids)) + " hrefs in " + str(cls.__collection_book_list))
            return True
        except Exception as e:
            logging.error("Failed to update " + str(len(book_ids)) + " hrefs in " + str(cls.__collection_book_list))
            # # logging.info(e)
            return False
    
    # Do the same but for the scraped reviews
    @classmethod
    def update_book_list_review_scraped(cls,book_ids):
        try:
            for book_id in book_ids:
                logging.info("Updating " + str(book_id) + " in " + str(cls.__collection_book_list) + " to review_scraped = 1")
                cls.__collection_book_list.update_one({"book_id": str(book_id)}, {"$set": {"review_scraped": 1}})
            logging.info("Updated " + str(len(book_ids)) + " hrefs in " + str(cls.__collection_book_list) + " to review_scraped = 1")
            return True
        except Exception as e:
            logging.error("Failed to update " + str(len(book_ids)) + " hrefs in " + str(cls.__collection_book_list) + " to review_scraped = 1")
            # # logging.info(e)
            return False

    # For the reviews we need to retrieve the review hrefs from the book list collection only if the review_scraped value is 0
    @classmethod
    def retrieve_review_hrefs_from_books(cls, amount):
        try:
            hrefs = []
            books = cls.__collection_book_list.find({"review_scraped": 0}).limit(amount)
            for book in books:
                hrefs.append(book['href'] + "/reviews")
            return hrefs
        except Exception as e:
            logging.error("Failed to retrieve books from " + str(cls.__collection_book_list))
            # logging.info(e)
            return False
        
    # We need to push the review data into the book reviews collection
    @classmethod
    def push_review_data_into_book_reviews(cls, dict_result):
        try:
            cls.__collection_book_reviews.insert_one(dict_result)
            logging.info("Inserted " + dict_result['book_id'] + " into " + str(cls.__collection_book_reviews))
            return True
        except Exception as e:
            logging.error("Failed to insert " + dict_result['book_id'] + " into " + str(cls.__collection_book_reviews))
            # logging.info(e)
            return False
    
    # fetch book info for data processing, leave amount as 0 to get all books
    @classmethod
    def get_books(cls, amount=0):
        if amount == 0:
            amount = cls.__collection_books.count()
        try:
            books = cls.__collection_books.find().limit(amount)
            return books
        except Exception as e:
            logging.error("Failed to retrieve books from " + str(cls.__collection_books))
            # logging.info(e)
            return False
    
    @classmethod
    def get_reviews(cls, amount=0):
        if amount == 0:
            amount = cls.__collection_book_reviews.count()
        try:
            reviews = cls.__collection_book_reviews.find().limit(amount)
            return reviews
        except Exception as e:
            logging.error("Failed to retrieve reviews from " + str(cls.__collection_book_reviews))
            # logging.info(e)
            return False

    # Very expensive method to scan a given collection to make sure every entry follows a given structure, if the structure is not followed, the entry is deleted
    # After deleting the entry, the method will return a list of the deleted entries 
    # Additionally the method will update the scraped value to 0 for the deleted entries coresponding to its collection
"""     @classmethod
    def verify_content_reviews(cls):
        try:
            deleted = []
            reviews = cls.__collection_book_reviews.find() """

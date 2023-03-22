"""

DONT USE THIS ONE

"""




""" from bs4 import BeautifulSoup
import urllib.request as urllib2
from mongo_handler import MongoReco

class review_scrape:

    __instance = None

    def __new__(self):
        if self.__instance is None:
            self.__instance = object.__new__(self)
        return self.__instance


    def get_rating_distribution(self):
        rating_distribution = {}
        for div in self.soup.findAll('div', {'class': 'RatingsHistogram__bar'}):
                number = div.text.split('star')[0]
                n_rev = div.find('div', {'class':'RatingsHistogram__labelTotal'}).text.split(' ')[0]
                n_rat = self.soup.find('span', {'data-testid':'ratingsCount'}).text
                t_n_rev = self.soup.find('span', {'data-testid':'reviewsCount'}).text
                rating_distribution[str(number) + 'star'] = n_rev
                rating_distribution['Ratings_Count'] = n_rat.split('\xa0ratings')[0]
                rating_distribution['Total_Review_Count'] = t_n_rev.split('\xa0reviews')[0]
        return rating_distribution


    def get_reviews(self):
        
        review_dictionary = {}
        for div in self.soup.findAll('article', {'class':'ReviewCard'}):
            name_user = div.find('div', {'class':'ReviewerProfile__name'})
            print(name_user.text)
            url = name_user.find('a').get('href')
            print(url)
            text = div.find('span', {'class': 'Formatted'})
            print(text.text)
            pivot_row = div.find('span', {'class': 'Text Text__body3'})
            review_id = pivot_row.find('a').get('href').split('/')[-1]
            print(review_id)
            review_dictionary['user_name'] = name_user.text
            review_dictionary['user_id'] = url.split('/')[-1]
            review_dictionary['text'] = text.text

        
        return review_dictionary
    
    def update_url(self, reviews_href):
        self.page_url = 'http://goodreads.com' + reviews_href
        self.page = urllib2.urlopen(self.page_url)
        self.soup = BeautifulSoup(self.page, 'html.parser')

    def wrapper(self, book_id, reviews_href):
        dict_result = {}
        self.update_url(reviews_href)
        reviews = self.get_reviews()
        ratings = self.get_rating_distribution()
        dict_result['book_id'] = book_id
        dict_result['reviews'] = reviews
        dict_result['ratings'] = ratings
        return dict_result
    
def review_provisioner(amount):
    r_hrefs = mongoreco.retrieve_review_hrefs_from_books(amount)
    for r_href in r_hrefs:
        book_id = r_href.split('/')[-2]
        dict_result = review_scraper.wrapper(book_id, r_href)
        success = mongoreco.push_review_data_into_book_reviews(dict_result)
        if success:
            print("Successfully pushed: " + str(dict_result['book_id']))
            mongoreco.update_book_list_review_scraped(book_id)
        else:
            print("Failed to push: " + str(dict_result['book_id']))
            print("Continuing to next book...")
    

if __name__ == "__main__":
    mongoreco = MongoReco()
    review_scraper = review_scrape()
    review_provisioner(100)


 """
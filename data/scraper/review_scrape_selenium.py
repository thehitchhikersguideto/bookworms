from bs4 import BeautifulSoup
import urllib.request as urllib2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from mongo_handler import MongoReco
import time
from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
import logging


class Page_Selenium:
    def __init__(self, page_url, driver):
        self.page_url = page_url
        self.page = driver.get(self.page_url)
    
    def get_HTML(self, driver):
        self.soup = BeautifulSoup(driver.page_source, 'html.parser')
        return self.soup
    
class Page_Beautiful_Soup:

    def __init__(self, page_url):
        self.page_url = page_url
        self.page = urllib2.urlopen(self.page_url)
        self.soup = BeautifulSoup(self.page, 'html.parser')
    
    def get_HTML(self):
        return self.soup
    

def get_rating_distribution(page):

    book_distribution = {}
    for div in page.findAll('div', {'class': 'RatingsHistogram__bar'}):
            number = div.text.split('star')[0]
            n_rev = div.find('div', {'class':'RatingsHistogram__labelTotal'}).text.split(' ')[0]
            n_rat = page.find('span', {'data-testid':'ratingsCount'}).text
            t_n_rev = page.find('span', {'data-testid':'reviewsCount'}).text
            book_distribution[str(number) + 'star'] = n_rev
            book_distribution['Ratings_Count'] = n_rat.split('\xa0ratings')[0]
            book_distribution['Total_Review_Count'] = t_n_rev.split('\xa0reviews')[0]
    return book_distribution

def get_reviews(page):

    reviews = {} 
    for div in page.findAll('article', {'class':'ReviewCard'}):
        name_user = div.find('div', {'class':'ReviewerProfile__name'})
        # print(name_user.text)
        url = name_user.find('a').get('href')
        # print(url)
        text = div.find('span', {'class': 'Formatted'})
        # print(text.text)
        pivot_row = div.find('span', {'class': 'Text Text__body3'})
        review_id = pivot_row.find('a').get('href').split('/')[-1]
        # print(review_id)
        reviews['user_name'] = name_user.text
        reviews['user_id'] = url.split('/')[-1]
        reviews['text'] = text.text
        reviews['book_id'] = book_id
        reviews['review_id'] = review_id
    
    return reviews

def checkForOverlay(driver):
    try:
        driver.find_element(By.CSS_SELECTOR, 'body > div.Overlay.Overlay--floating')
        try:
            element = driver.find_element(By.CSS_SELECTOR, 'body > div.Overlay.Overlay--floating > div > div.Overlay__header > div')
            if element.is_displayed() and element.is_enabled():
                print("Overlay handled")
                element.click()
                return False
                
        except Exception as e:
            print("Overlay Error")
            print(e)
            return True
    except:
        print("No Overlay")
        return False

def wrapper(book_id, page):
    dict_result = {}
    reviews = get_reviews(page)
    ratings = get_rating_distribution(page)
    dict_result['book_id'] = book_id
    dict_result['reviews'] = reviews
    dict_result['ratings'] = ratings
    return dict_result

def url_constructor(href):
    page_url = 'http://goodreads.com' + href
    return page_url 

if __name__ == "__main__":
    
    bookReviews_list = []
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--start-maximized")
    seleniumLogger.setLevel(logging.WARNING)
    driver = webdriver.Chrome(executable_path=r'C:\Users\ismae\Desktop\Selenium-bots\Drivers\chromedriver.exe', chrome_options=chrome_options)
    mongo_reco = MongoReco()
    review_hrefs = mongo_reco.retrieve_review_hrefs_from_books(100)
    for href in review_hrefs:
        p = Page_Selenium(url_constructor(href), driver)
        checkForOverlay(driver)
        time.sleep(3)
        page = Page_Selenium.get_HTML(p, driver)
        book_id = href.split('/')[-2]
        output = wrapper(book_id, page)
        success = mongo_reco.push_review_data_into_book_reviews(output)
        if success:
            print("Successfully pushed: " + str(output['book_id']))
            print("------Book ID------", book_id)
            mongo_reco.update_book_list_review_scraped([book_id])
        else:
            print("Failed to push: " + str(output['book_id']))
            print("Continuing to next book...")



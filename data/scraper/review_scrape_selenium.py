from bs4 import BeautifulSoup
import urllib.request as urllib2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from mongo_handler import MongoReco
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
import logging


class review_scrape:
    
    __instance = None
    def __init__(self, driver):
        self.html = None
        self.soup = None
        self.driver = driver
        self.href = None
        self.url = None
        self.book_id = None

    def set_book_id(self, book_id):
        self.book_id = book_id

    def set_soup(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')

    def set_url(self, href):
        self.url = "https://goodreads.com" + href

    def set_driver(self, driver):
        self.driver = driver

    def set_html(self, html):
        self.html = html
    
    def set_href(self, href):
        self.href = href

    def get_href(self):
        return self.href
    
    def get_book_id(self):
        return self.book_id
    
    def get_driver(self):
        return self.driver

    def get_url(self):
        return self.url

    def get_html(self):
        return self.html

    def get_soup(self):
        return self.soup
    
    def update(self, href):
        self.set_href(href)
        self.set_url(self.get_href())
        self.set_book_id(self.get_url().split('/')[-2])

        
    def update_html(self, driver):
        self.set_html(driver.page_source)
        self.set_soup(self.get_html())
        

    def get_rating_distribution(self):

        book_distribution = {}
        for div in self.soup.findAll('div', {'class': 'RatingsHistogram__bar'}):
                number = div.text.split('star')[0]
                n_rev = div.find('div', {'class':'RatingsHistogram__labelTotal'}).text.split(' ')[0]
                n_rat = self.soup.find('span', {'data-testid':'ratingsCount'}).text
                t_n_rev = self.soup.find('span', {'data-testid':'reviewsCount'}).text
                book_distribution[str(number) + 'star'] = n_rev
                book_distribution['Ratings_Count'] = n_rat.split('\xa0ratings')[0]
                book_distribution['Total_Review_Count'] = t_n_rev.split('\xa0reviews')[0]
        return book_distribution

    def get_reviews(self):

        reviews = {} 
        for div in self.soup.findAll('article', {'class':'ReviewCard'}):
            name_user = div.find('div', {'class':'ReviewerProfile__name'})
            #print(name_user.text)
            try:
                url = name_user.find('a').get('href')
                #print(url)
            
            except Exception:
                #print("No URL")
                url = None

            # print(url)
            try:
                text = div.find('span', {'class': 'Formatted'})
            
            except Exception:
                #print("No text")
                text = None
            # print(text.text)

            try:
                pivot_row = div.find('span', {'class': 'Text Text__body3'})
            except Exception:
                pivot_row = None
            
            try:
                review_id = pivot_row.find('a').get('href').split('/')[-1]
                #print(review_id)
            except Exception:
                review_id = None

            try:
                rating = div.find('span', {'class': 'RatingStars RatingStars__small'})
                rating = rating['aria-label']
                rating = rating.split(' ')[1] + ' star'
            except Exception:
                rating = None

            # print(review_id)
            reviews[str(review_id)] = {}
            reviews[str(review_id)]['user_name'] = name_user.text
            reviews[str(review_id)]['user_id'] = url.split('/')[-1]
            reviews[str(review_id)]['text'] = text.text
            reviews[str(review_id)]['rating'] = rating
            logging.info(rating)
            logging.info(reviews[str(review_id)]['text'][:10])
            
        
        return reviews
    
def manage_overlay(driver, count = 0):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ReviewText__content')))
        try:
            driver.find_element(By.CSS_SELECTOR, 'body > div.Overlay.Overlay--floating')
            try:
                element = driver.find_element(By.CSS_SELECTOR, 'body > div.Overlay.Overlay--floating > div > div.Overlay__header > div')
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    logging.info("Overlay Closed")
                    return False
                        
            except Exception as e:
                logging.info("Overlay Error or Overlay Closed Already")
                # print(e)
                return True
        except:
            print("No Overlay")
            return False
    except:
        if count == 1:
            logging.info("Loading Error")
            return True
        logging.info("Loading longer than expected")
        logging.info("Trying again")
        count += 1
        manage_overlay(driver, count)


if __name__ == "__main__":

    mongoreco = MongoReco()
    
    chrome_options = Options()
    chrome_options.page_load_strategy = 'normal'
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    seleniumLogger.setLevel(logging.WARNING)
    driver = webdriver.Chrome(executable_path=r'\data\scraper\Drivers\chromedriver.exe', chrome_options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    review_scraper = review_scrape(driver)
    review_hrefs = mongoreco.retrieve_review_hrefs_from_books(20)

    for href in review_hrefs:
        review_scraper.update(href)
        driver.get(review_scraper.get_url())
        over_lay_error = manage_overlay(driver)
        if not over_lay_error:
            review_scraper.update_html(driver)
            reviews = review_scraper.get_reviews()
            ratings = review_scraper.get_rating_distribution()
            success = mongoreco.push_review_data_into_book_reviews({"book_id": review_scraper.get_book_id(), "reviews": reviews, "ratings": ratings})
            if success:
                mongoreco.update_book_list_review_scraped([review_scraper.get_book_id()])
            # logging.info("")
            continue
        logging.info("Skipping href: " + href)
        logging.info("Skip caused by overlay error")
        continue

    logging.info("Finished scraping " + str(len(review_hrefs)) + " reviews")
    logging.info("Closing driver")
    driver.quit()


    
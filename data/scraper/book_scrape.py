from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import bs4
from mongo_handler import MongoReco
import logging
import datetime 
from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class book_scrape:

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
        self.soup = bs4.BeautifulSoup(html, 'html.parser')
    
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
        self.set_book_id(self.get_href().split('/')[-1])
        

    def update_soup(self):
        self.set_html(self.driver.page_source)
        self.set_soup(self.get_html())

    def get_series_name(self):
        try:
            # Find element by css selector
            soup = self.soup.find_all('div',class_ = "DescListItem")
            for item in soup:
                if item.find('dt').text == 'Series':
                    soup = item.find('a').text
                    return soup

        except Exception as e:
            logging.info(e)
            return None
        
    def get_isbn(self):
        try:
            # Find element by css selector
            soup = self.soup.find_all('div',class_ = "DescListItem")
            for item in soup:
                if item.find('dt').text == 'ISBN':
                    soup = item.find('div', class_ = 'TruncatedContent__text TruncatedContent__text--small').text
                    # only grab the first 13 characters
                    soup = soup[:13]
                    return soup

        except Exception as e:
            logging.info(e)
            return None

    def get_language(self):
        try:
            # Find element by css selector
            soup = self.soup.find_all('div',class_ = "DescListItem")
            for item in soup:
                if item.find('dt').text == 'Language':
                    soup = item.find('div', class_ = 'TruncatedContent__text TruncatedContent__text--small').text
                    return soup

        except Exception as e:
            logging.info(e)
            return None

    def get_pages(self):
        try:
            # Find element by css selector
            soup = self.soup.find_all('div',class_ = "DescListItem")
            for item in soup:
                if item.find('dt').text == 'Format':
                    soup = item.find('div', class_ = 'TruncatedContent__text TruncatedContent__text--small').text
                    # grab elements before the first space
                    soup = soup.split(' ')[0]
                    return soup

        except Exception as e:
            logging.info(e)
            return None

    def get_publish_date(self):
        try:
            # Find element by css selector
            soup = self.soup.find_all('div',class_ = "DescListItem")
            for item in soup:
                if item.find('dt').text == 'Publisher':
                    soup = item.find('div', class_ = 'TruncatedContent__text TruncatedContent__text--small').text
                    # Only take the string before the word by (if it exists)
                    if 'by' in soup:
                        soup = soup.split(' by ')[0]
                    return soup
                

        except Exception as e:
            logging.info(e)
            return None, None

    def get_publisher_year_published(self):
        try:
            # Find element by css selector
            soup = self.soup.find_all('div',class_ = "DescListItem")
            for item in soup:
                if item.find('dt').text == 'Published':
                    print("Found Published")
                    soup = item.find('div', class_ = 'TruncatedContent__text TruncatedContent__text--small').text
                    print("Soup = ", soup)
                    # return two items, publisher and date published
                    if 'by' in soup:                                                                                
                        date, publisher = soup.split(' by ')
                        print("Date = ", date)
                        print("Publisher = ", publisher)
                        return date, publisher
                    return soup, None
            return None, None
            
            

        except Exception as e:
            logging.info(e)
            return None, None
        
    def get_primary_lists(self):
        try:
            # List : href
            lists = {}
            # Find element by css selector
            soup = self.soup.find('div',class_ = "CarouselGroup")
            for list in soup:
                href = list.find('a')['href']
                name = list.find('h3').find('span').text
                lists[name] = href
                
            return lists

        except Exception as e:
            logging.info(e)
            return None
        
    def get_all_lists_link(self):
        try:
            soup = self.soup.find('a',class_ = "Button Button--inline Button--small", attrs={'aria-label': 'Tap to show all lists featuring this book'})['href']
            return soup

        except Exception as e:
            logging.info(e)
            return None
        
    def get_rating(self):
        try:
            soup = self.soup.find('div',class_ = "RatingStatistics__rating").text
            return soup

        except Exception as e:
            logging.info(e)
            return None

    def get_num_reviews(self):
        try:
            soup = self.soup.find('span',attrs = {"data-testid":"reviewsCount"}).text
            # only take before the word reviews
            soup = soup.split(' reviews')[0].split('\xa0')[0]
            return soup

        except Exception as e:
            logging.info(e)
            return None

    def get_num_ratings(self):
        try:
            soup = self.soup.find('span',attrs = {"data-testid":"ratingsCount"}).text
            # only take before the word reviews
            soup = soup.split(' ratings')[0].split('\xa0')[0]
            return soup

        except Exception as e:
            logging.info(e)
            return None

    def get_awards(self):
        # Award : href
        awards = {}
        try:
            # Find element by css selector
            soup = self.soup.find_all('div',class_ = "DescListItem")
            for item in soup:
                if item.find('dt').text == 'Literary awards':
                    soup = item.find('div', class_ = 'TruncatedContent__text TruncatedContent__text--small')
                    for award in soup:
                        if type(award) == bs4.element.Tag:
                            href = award.find('a')['href']
                            name = award.find('a').text
                            awards[name] = href
                        else:
                            pass
                        
                        
            return awards

        except Exception as e:
            logging.info(e)
            return None

    def get_author(self):
        try:
            soup = self.soup.find('a',class_ = "ContributorLink").text
            return soup

        except Exception as e:
            logging.info(e)
            return None

    def get_price(self):
        try:
            soup = self.soup.find('div', class_ = 'BookActions__button')
            # get sibling of self.soup
            soup = soup.find_next_sibling('div').text
            # after dollar sign
            soup = soup.split('$')[1]
            return soup

        except Exception as e:
            logging.info(e)
            return None

    def get_genres(self):
        # Genre : href
        genres = {}
        try:
            # Find element by css selector
            soup = self.soup.find_all('span', class_ = 'BookPageMetadataSection__genreButton')
            for genre in soup:
                if type(genre) == bs4.element.Tag:
                    href = genre.find('a')['href']
                    name = genre.find('a').find('span').text
                    genres[name] = href
                else:
                    pass
                        
                        
                        
            return genres

        except Exception as e:
            logging.info(e)
            return None
        
    def get_description(self):
        try:
            soup = self.soup.find('div', class_ = 'BookPageMetadataSection__description').find('span', class_ = 'Formatted').text
            return soup

        except Exception as e:
            logging.info(e)
            return None

    def get_title(self):
        try:
            soup = self.soup.find('h1', class_ = 'Text Text__title1').text
            return soup

        except Exception as e:
            logging.info(e)
            return None

    def get_current_readers(self):
        try:
            soup = self.soup.find('div', class_ = 'SocialSignalsSection__caption', attrs = {'data-testid':'currentlyReadingSignal'}).text
            # only take before the word reviews
            soup = soup.split(' ')[0]
            return soup

        except Exception as e:
            logging.info(e)
            return None
        
    def get_date_time_of_scrape(self):
        return datetime.datetime.now().isoformat()

    def get_wanted_to_read(self):
        try:
            soup = self.soup.find('div', class_ = 'SocialSignalsSection__caption', attrs = {'data-testid':'toReadSignal'}).text
            # only take before the word reviews
            soup = soup.split(' ')[0]
            return soup

        except Exception as e:
            logging.info(e)
            return None
        
    def scrape_wrapper(self):
        # get all the data
        data = {}
        data['book_id'] = self.book_id
        data['title'] = self.get_title()
        data['author'] = self.get_author()
        data['price'] = self.get_price()
        data['genres'] = self.get_genres()
        data['isbn'] = self.get_isbn()
        data['language'] = self.get_language()
        data['series'] = self.get_series_name()
        data['publisher'] = self.get_publisher_year_published()[1]
        data['year_published'] = self.get_publisher_year_published()[0]
        data['description'] = self.get_description()
        data['current_readers'] = self.get_current_readers()
        data['wanted_to_read'] = self.get_wanted_to_read()
        data['num_reviews'] = self.get_num_reviews()
        data['num_ratings'] = self.get_num_ratings()
        data['rating'] = self.get_rating()
        data['awards'] = self.get_awards()
        data['primary_lists'] = self.get_primary_lists()
        data['all_lists_link'] = self.get_all_lists_link()
        data['date_time_of_scrape'] = self.get_date_time_of_scrape()

        return data
    
    def expand_everything(self):
        try:
            # Using this css selector to find the button then click it 
            # driver.implicitly_wait(2)
            # div.CollapsableList > div:nth-child(3) > button:nth-child(1) > span:nth-child(1)
            # scroll to the top
            # driver.execute_script("window.scrollTo(0, 0);")
            #element2 = driver.find_element(By.CSS_SELECTOR, '{class_ = "Button__labelItem"}')
            # element = driver.find_element(By.XPATH, "//span[text()='Book details & editions']")
            element = self.driver.find_element(By.CSS_SELECTOR, '#__next > div > main > div.BookPage__gridContainer > div.BookPage__rightColumn > div.BookPage__mainContent > div.BookPageMetadataSection > div.BookDetails > div > div > button > span:nth-child(1)')
            # Scroll to button
            # AC(driver).scroll_to_element(element).perform()
            #AC(driver).move_to_element(element).perform()
            # driver.execute_script("arguments[0].scrollIntoView(false);", element)
            # AC(driver).scroll_by_amount(0,-100).move_to_element(element).perform()
            # wait for the button to be visible
            # check if the button is visible
            if element.is_displayed() and element.is_enabled():
                element.click()
                # Implicit wait 
                # Save the html as a file
                return True
        except Exception as e:
            if 'Unable to locate element: {"method":"css selector","selector":"#__next > div > main > div.BookPage__gridContainer > div.BookPage__rightColumn > div.BookPage__mainContent > div.BookPageMetadataSection > div.BookDetails > div > div > button > span:nth-child(1)"}' in str(e):
                logging.info("Unable to find book details button, skipping this href")
                logging.info(e)
                # logging.info(driver.page_source)
                return False
            logging.info(e)
            return False
        
    def load_lists_functional(self, count = 0):
            # scroll to the bottom of the page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                self.driver.find_element(By.CSS_SELECTOR, '[class="CarouselGroup"]')
                return True
            except Exception as e:
                logging.info("Lists not yet loaded, continuing scroll")
                if count < 50:
                    if count % 10 == 0:
                        logging.info("Lists not yet loaded, continuing scroll")
                    if count % 20 == 0:
                        self.driver.refresh()
                    count += 1
                    self.load_lists_functional(count)
                return False
            
    def load_lists_expiremental(self):
        count = 0
        while EC.visibility_of_element_located((By.CSS_SELECTOR, '[class="CarouselGroup"]')) != True and count < 20:
            time.sleep(0.5)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            count += 1
        if count == 20:
            self.driver.refresh()
            self.html_expansion_wrapper()
        else:
            logging.info("Lists loaded after " + str(count/2 ) + " seconds")
            return True

    def html_expansion_wrapper(self):
        if self.expand_everything() and self.load_lists_functional():
            return True
        else:
            return False

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
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    seleniumLogger.setLevel(logging.WARNING)
    driver = webdriver.Chrome(executable_path=r'\data\scraper\Drivers\chromedriver.exe', chrome_options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.implicitly_wait(10)
    book_scraper = book_scrape(driver)
    book_batch = mongoreco.retrieve_books_from_book_lists(50)
    counter = 0
    for book in book_batch:
        book_scraper.update(book)
        driver.get(book_scraper.get_url())
        over_lay_error = manage_overlay(driver)
        if not over_lay_error:
            book_scraper.expand_everything()
            book_scraper.load_lists_functional()
            book_scraper.update_soup()
            data = book_scraper.scrape_wrapper()
            success = mongoreco.insert_into_books(data)
            if success:
                logging.info("Successfully Inserted: " + data['title'])
                counter += 1
                logging.info(str(counter) + " books scraped out of " + str(len(book_batch)))
                mongoreco.update_book_list_book_scraped([book_scraper.get_book_id()])
            continue
        logging.info("Skipping href: " + book_scraper.get_href())
        logging.info("Skip caused by overlay error")
        continue
    logging.info("Finished scraping " + str(len(book_batch)) + " books")
    logging.info("Closing driver")
    driver.quit()
import argparse
from datetime import datetime
import json
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC
import pymongo
from bson import BSON
from dotenv import load_dotenv

from urllib.request import urlopen
from urllib.error import HTTPError
import bs4
import os


def initSoup(html):
    print('Initializing soup...')
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup

def get_id(book_id):
    return book_id.split('.')[0]

def get_series_name(soup):
    try:
        # Find element by css selector
        soup = soup.find_all('div',class_ = "DescListItem")
        for item in soup:
            if item.find('dt').text == 'Series':
                soup = item.find('a').text
                return soup

    except Exception as e:
        print(e)
        return None
    
def get_isbn(soup):
    try:
        # Find element by css selector
        soup = soup.find_all('div',class_ = "DescListItem")
        for item in soup:
            if item.find('dt').text == 'ISBN':
                soup = item.find('div', class_ = 'TruncatedContent__text TruncatedContent__text--small').text
                # only grab the first 13 characters
                soup = soup[:13]
                return soup

    except Exception as e:
        print(e)
        return None

def get_language(soup):
    try:
        # Find element by css selector
        soup = soup.find_all('div',class_ = "DescListItem")
        for item in soup:
            if item.find('dt').text == 'Language':
                soup = item.find('div', class_ = 'TruncatedContent__text TruncatedContent__text--small').text
                return soup

    except Exception as e:
        print(e)
        return None

def get_pages(soup):
    try:
        # Find element by css selector
        soup = soup.find_all('div',class_ = "DescListItem")
        for item in soup:
            if item.find('dt').text == 'Format':
                soup = item.find('div', class_ = 'TruncatedContent__text TruncatedContent__text--small').text
                # grab elements before the first space
                soup = soup.split(' ')[0]
                return soup

    except Exception as e:
        print(e)
        return None

def get_publish_date(soup):
    try:
        # Find element by css selector
        soup = soup.find_all('div',class_ = "DescListItem")
        for item in soup:
            if item.find('dt').text == 'Publisher':
                soup = item.find('div', class_ = 'TruncatedContent__text TruncatedContent__text--small').text
                # Only take the string before the word by (if it exists)
                if 'by' in soup:
                    soup = soup.split(' by ')[0]
                return soup
            

    except Exception as e:
        print(e)
        return None, None

def get_publisher_year_published(soup):
    try:
        # Find element by css selector
        soup = soup.find_all('div',class_ = "DescListItem")
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
        print("Not found Published")
        return None, None
        
        

    except Exception as e:
        print(e)
        return None, None
    
def get_primary_lists(soup):
    try:
        # List : href
        lists = {}
        # Find element by css selector
        soup = soup.find('div',class_ = "CarouselGroup")
        for list in soup:
            href = list.find('a')['href']
            name = list.find('h3').find('span').text
            lists[name] = href
            
        return lists

    except Exception as e:
        print(e)
        return None
    
def get_all_lists_link(soup):
    try:
        soup = soup.find('a',class_ = "Button Button--inline Button--small", attrs={'aria-label': 'Tap to show all lists featuring this book'})['href']
        return soup

    except Exception as e:
        print(e)
        return None
    
def get_rating(soup):
    try:
        soup = soup.find('div',class_ = "RatingStatistics__rating").text
        return soup

    except Exception as e:
        print(e)
        return None

def get_num_reviews(soup):
    try:
        soup = soup.find('span',attrs = {"data-testid":"reviewsCount"}).text
        # only take before the word reviews
        soup = soup.split(' reviews')[0].split('\xa0')[0]
        return soup

    except Exception as e:
        print(e)
        return None

def get_num_ratings(soup):
    try:
        soup = soup.find('span',attrs = {"data-testid":"ratingsCount"}).text
        # only take before the word reviews
        soup = soup.split(' ratings')[0].split('\xa0')[0]
        return soup

    except Exception as e:
        print(e)
        return None

def get_awards(soup):
    # Award : href
    awards = {}
    try:
        # Find element by css selector
        soup = soup.find_all('div',class_ = "DescListItem")
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
        print(e)
        return None

def get_author(soup):
    try:
        soup = soup.find('a',class_ = "ContributorLink").text
        return soup

    except Exception as e:
        print(e)
        return None

def get_price(soup):
    try:
        soup = soup.find('div', class_ = 'BookActions__button')
        # get sibling of soup
        soup = soup.find_next_sibling('div').text
        # after dollar sign
        soup = soup.split('$')[1]
        return soup

    except Exception as e:
        print(e)
        return None

def get_genres(soup):
    # Genre : href
    genres = {}
    try:
        # Find element by css selector
        soup = soup.find_all('span', class_ = 'BookPageMetadataSection__genreButton')
        for genre in soup:
            if type(genre) == bs4.element.Tag:
                href = genre.find('a')['href']
                name = genre.find('a').find('span').text
                genres[name] = href
            else:
                pass
                    
                    
                    
        return genres

    except Exception as e:
        print(e)
        return None
    
def get_description(soup):
    try:
        soup = soup.find('div', class_ = 'BookPageMetadataSection__description').find('span', class_ = 'Formatted').text
        return soup

    except Exception as e:
        print(e)
        return None

def get_title(soup):
    try:
        soup = soup.find('h1', class_ = 'Text Text__title1').text
        return soup

    except Exception as e:
        print(e)
        return None

def get_current_readers(soup):
    try:
        soup = soup.find('div', class_ = 'SocialSignalsSection__caption', attrs = {'data-testid':'currentlyReadingSignal'}).text
        # only take before the word reviews
        soup = soup.split(' ')[0]
        return soup

    except Exception as e:
        print(e)
        return None
    
def get_wanted_to_read(soup):
    try:
        soup = soup.find('div', class_ = 'SocialSignalsSection__caption', attrs = {'data-testid':'toReadSignal'}).text
        # only take before the word reviews
        soup = soup.split(' ')[0]
        return soup

    except Exception as e:
        print(e)
        return None

def soupProvisioner(html):
    soup = initSoup(html)
    title = get_title(soup)
    series = get_series_name(soup)
    isbn = get_isbn(soup)
    language = get_language(soup)
    pages = get_pages(soup)
    publisher = get_publisher_year_published(soup)[1]
    year_published = get_publisher_year_published(soup)[0]
    lists = get_primary_lists(soup)
    list_link = get_all_lists_link(soup)
    rating = get_rating(soup)
    reviews = get_num_reviews(soup)
    ratings = get_num_ratings(soup)
    awards = get_awards(soup)
    author = get_author(soup)
    price = get_price(soup)
    genres = get_genres(soup)
    description = get_description(soup)
    current_readers = get_current_readers(soup)
    wanted_to_read = get_wanted_to_read(soup)

    print("Title: ",title)
    print("Series: ",series)
    print("ISBN: ",isbn)
    print("Language: ",language)
    print("Pages: ",pages)
    print("Publisher: ",publisher)
    print("Date published: ",year_published)
    print("Lists: ",lists)
    print("List Link: ",list_link)
    print("Rating: ",rating)
    print("Reviews: ",reviews)
    print("Ratings: ",ratings)
    print("Awards: ",awards)
    print("Authors: ",author)
    print("Price: ",price)
    print("Genres: ",genres)
    print("Description: ",description)
    print("Current Readers: ",current_readers)
    print("Wants to Read: ",wanted_to_read)

    result = {
        'Title': title,
        'Series_name': series,
        'ISBN': isbn,
        'Language': language,
        'Pages': pages,
        'Publisher': publisher,
        'Year_published': year_published,
        'Primary_lists': lists,
        'All_lists_link': list_link,
        'Rating': rating,
        'Num_reviews': reviews,
        'Num_ratings': ratings,
        'Awards': awards,
        'Author': author,
        'Price': price,
        'Genres': genres,
        'Description': description,
        'Current_readers': current_readers,
        'Wanted_to_read': wanted_to_read
    }
    return result



def loadEnvVars():
    # Load MongoDB credentials from .env file
    if os.environ.get('password') and os.environ.get('user'):
        del os.environ["password"]
        del os.environ["user"]
    
    load_dotenv()
    password = os.environ.get('password')
    user = os.environ.get('user')
    print("Password: ",password)
    print("User: ",user)
    return password, user

def loadMongo(password,user):
    SOURCE_DB = 'Goodreads'
    SOURCE_COLLECTION = 'Books'
    MONGO_URI = f"mongodb+srv://{user}:{password}@recosystems.hyjorhd.mongodb.net/?retryWrites=true&w=majority"
    print(MONGO_URI)
    client = pymongo.MongoClient(MONGO_URI)
    db = client[SOURCE_DB]
    collection = db[SOURCE_COLLECTION]
    return collection

# MongoDB requires special characters to be encoded in the URI (% + ASCII code)

def startMongo():
    password, user = loadEnvVars()
    collection = loadMongo(password,user)
    return collection



def insertIntoMongo(collection, jsonResult):
    try:
        collection.insert_many(jsonResult)
        for i in range(len(jsonResult)):
            print("Successfully inserted " + jsonResult[i]['Title'] + " into MongoDB")
        return True
    except Exception as e:
        print(e)
        for i in range(len(jsonResult)):
            print("Failed to insert " + jsonResult[i]['Title'] + " into MongoDB")
        return False
    
# Selenium Setup
def initDriver(startingBook):
    chrome_options = Options()
    chrome_options.page_load_strategy = 'normal'
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://www.goodreads.com/book/show/'+startingBook)
    driver.implicitly_wait(10)
    # wait until the page is fully loaded
    print("Refresh")
    driver.refresh()
    return driver

def feed(driver, book):
    driver.get("https://www.goodreads.com/book/show/" + book)
    print("Feeding " + book)

def checkForOverlay(driver):
    try:
        driver.find_element(By.CSS_SELECTOR, 'body > div.Overlay.Overlay--floating')
        try:
            element = driver.find_element(By.CSS_SELECTOR, 'body > div.Overlay.Overlay--floating > div > div.Overlay__header > div')
            if element.is_displayed() and element.is_enabled():
                print("Overlay")
                element.click()
                return False
                
        except Exception as e:
            print("Overlay Error")
            print(e)
            return True
    except:
        print("No Overlay")
        return False
        
 
def loadLists(driver):
    # scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    try:
        driver.find_element(By.CSS_SELECTOR, '[class="CarouselGroup"]')
    except Exception as e:
        print("Lists not yet loaded, continuing scroll")
        
        loadLists(driver)

def bookHandler(fileHandler, block_size=10):
    # python generator to read line from books.txt and yield the line
    block = []
    for line in fileHandler:
        line = line.strip()
        block.append(line)
        if len(block) == block_size:
            yield block
            block = []

    if block:
        yield block



def expandEverything(driver):
     #while not checkForOverlay(driver):
        try:
            # Using this css selector to find the button then click it 
            # driver.implicitly_wait(2)
            # div.CollapsableList > div:nth-child(3) > button:nth-child(1) > span:nth-child(1)
            # scroll to the top
            # driver.execute_script("window.scrollTo(0, 0);")
            #element2 = driver.find_element(By.CSS_SELECTOR, '{class_ = "Button__labelItem"}')
            # element = driver.find_element(By.XPATH, "//span[text()='Book details & editions']")
            element = driver.find_element(By.CSS_SELECTOR, '#__next > div > main > div.BookPage__gridContainer > div.BookPage__rightColumn > div.BookPage__mainContent > div.BookPageMetadataSection > div.BookDetails > div > div > button > span:nth-child(1)')
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

            print(e)
            return False
    

def provisioner(driver, book):
    # feed the driver the book
    feed(driver, book)
    # expand everything
    expandEverything(driver)
    html = driver.page_source
    driver.quit()
    return html

def MasterHandling():
    collection = startMongo()
    with open('booksUnique.txt') as fileHandler:
        for book in bookHandler(fileHandler):
            driver = initDriver(book[0])
            result = []
            for b in book:
                feed(driver, b)
                checkForOverlay(driver)
                expandEverything(driver)
                loadLists(driver)
                html = driver.page_source
                result.append(soupProvisioner(html))
                if len(result) == 10:
                    insertIntoMongo(collection, result)
                    result = []
            driver.quit()

def writeHtmltoFile(html):
    # create new file
    f = open("test.html", "w", encoding="utf-8")
    # write to file
    f.write(html)
    # close file
    f.close()


    

def MasterHandlingTest():
    with open('bookstest.txt') as fileHandler:
        for book in bookHandler(fileHandler):
            driver = initDriver(book[0])
            for b in book:
                feed(driver, b)
                checkForOverlay(driver)
                expandEverything(driver)
                loadLists(driver)
                html = driver.page_source
                writeHtmltoFile(html)
                result = soupProvisioner(html)    
                insertIntoMongo(result)
                print(result)
            driver.quit()
            
if __name__ == "__main__":
    MasterHandling()
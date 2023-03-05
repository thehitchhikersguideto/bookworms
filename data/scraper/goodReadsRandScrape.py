from urllib.request import urlopen
import bs4
import logging

logging.basicConfig(
        filemode="w"
    )


# Using beautiful soup load our initial page

# Our starting page is the genres list
# https://www.goodreads.com/genres/list
# On each page we want to go thrrough each genre and get the top 100 books
# We want to automatically fetch each genre page

# Grab the genres with the a class, only return the href
def grab_genres(page = 1):
    if page == 1:
        source = urlopen('https://www.goodreads.com/genres/list')
    else:
        source = urlopen('https://www.goodreads.com/genres/list?page=' + str(page))
    soup = bs4.BeautifulSoup(source, 'lxml')
    logging.basicConfig(filename='goodReadsRandScrape.log', level=logging.DEBUG)
    genres = [node['href'] for node in soup.find_all('a', {'class': 'mediumText actionLinkLite'})]
    # Remove the /genres/ from the href
    genres = [genre.split('/')[-1] for genre in genres]
    # Log the genres
    if genres:
        logging.info("Fetched genres")
        logging.info("Genre count: " + str(len(genres)))
        logging.info("Genres: " + str(genres[:5]) + "...")
    return genres

def grab_lists(genre):
    logging.info("Fetching lists for " + genre)
    source = urlopen('https://www.goodreads.com/list/tag/' + genre)
    soup = bs4.BeautifulSoup(source, 'lxml')
    listTags = [node['href'] for node in soup.find_all('a', {'class': 'listTitle'})]
    if listTags:
        logging.info("Fetched lists")
        logging.info("List count: " + str(len(listTags)))
        logging.info("Lists: " + str(listTags[:5]) + "...")
    else:
        logging.info("No lists found")
    return listTags

def grab_books(listTag):
    logging.info("Fetching books for " + listTag)
    source = urlopen('https://www.goodreads.com' + listTag)
    soup = bs4.BeautifulSoup(source, 'lxml')
    bookList = [node['href'] for node in soup.find_all('a', {'class': 'bookTitle'})]
    if bookList:
        logging.info("Fetched books")
        logging.info("Book count: " + str(len(bookList)))
        logging.info("Books: " + str(bookList[:5]) + "...")
    else:
        logging.info("No books found")
    return bookList


# Got to the genre page
def fetchBooks():
    # For loop representing the pages of genres, 1-14
    for i in range(1, 15):
        genres = grab_genres()
        for genre in genres:
            lists = grab_lists(genre)
            logging.info("List count: " + str(len(lists)))
            count = 0
            for list in lists:
                books = grab_books(list)
                logging.info("Book count: " + str(len(books)))
                # Write to href of each book to a file
                with open('books.txt', 'a') as f:
                    for book in books:
                        if count == 500:
                            break
                        # Remove the /book/show/ from the href
                        book = book.split('/')[-1]
                        # Add a new line inbetween each book
                        f.write(book + '\n')

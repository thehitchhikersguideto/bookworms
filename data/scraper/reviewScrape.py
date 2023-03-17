from bs4 import BeautifulSoup
import urllib.request as urllib2


class Page:

    def __init__(self, page_url):
        self.page_url = page_url
        self.page = urllib2.urlopen(self.page_url)
        self.soup = BeautifulSoup(self.page, 'html.parser')
    
    def get_HTML(self):
        return self.soup

def get_rating_distribution(page, book_id, book_distribution):

    for div in page.findAll('div', {'class': 'RatingsHistogram__bar'}):
            number = div.text.split('star')[0]
            n_rev = div.find('div', {'class':'RatingsHistogram__labelTotal'}).text.split(' ')[0]
            n_rat = page.find('span', {'data-testid':'ratingsCount'}).text
            t_n_rev = page.find('span', {'data-testid':'reviewsCount'}).text
            book_distribution[str(book_id)][str(number) + 'star'] = n_rev
            book_distribution[str(book_id)]['Ratings_Count'] = n_rat.split('\xa0ratings')[0]
            book_distribution[str(book_id)]['Total_Review_Count'] = t_n_rev.split('\xa0reviews')[0]
    return book_distribution

def get_reviews(page, book_id, reviews):
     
    for div in page.findAll('article', {'class':'ReviewCard'}):
        name_user = div.find('div', {'class':'ReviewerProfile__name'})
        print(name_user.text)
        url = name_user.find('a').get('href')
        print(url)
        text = div.find('span', {'class': 'Formatted'})
        print(text.text)
        pivot_row = div.find('span', {'class': 'Text Text__body3'})
        review_id = pivot_row.find('a').get('href').split('/')[-1]
        print(review_id)
        reviews[review_id] = {}
        reviews[review_id]['user_name'] = name_user.text
        reviews[review_id]['user_id'] = url.split('/')[-1]
        reviews[review_id]['text'] = text.text
        reviews[review_id]['book_id'] = book_id
    
    return reviews

     
if __name__ == "__main__":
    book_distribution = {}
    reviews = {}
    books_ids = ['BOOK_IDS']
    pages = ['URLS']
    for book_id, i in zip(books_ids, pages):
        p = Page(i)
        page = Page.get_HTML(p)
        book_distribution[book_id] = {}
        book_distribution = get_rating_distribution(page, book_id, book_distribution)
        reviews = get_reviews(page, book_id, reviews)
    
    print(book_distribution)
    print()
    print(reviews)
# imports
from utils import load_model
from utils import cosine_similarity_content
from utils import load_data_for_cosine_sim
from utils import load_data_for_rating_prediction
from utils import get_rating_prediction
from utils import get_top_k_books
from utils import xgb_preprocess

import pandas as pd

xgboost = load_model()



def user_books(): 
    """Input of books based on user preference"""
    # Get user input
    # TODO: Connnect to frontend 
    user_books_ids = ['77203.The_Kite_Runner', '929.Memoirs_of_a_Geisha', '128029.A_Thousand_Splendid_Suns', '19063.The_Book_Thief', '4214.Life_of_Pi']
    user_ratings = [4, 4, 3, 5, 4]
    books_to_return=500
    return user_books_ids, user_ratings, books_to_return

def get_cosine_sim(user_info): 
    user_books_ids, user_ratings, books_to_return = user_info
    top_k_books = cosine_similarity_content.get_cosine_recommendations(user_books_ids, user_ratings, books_to_return)
    return top_k_books

def prepare_data_for_rating_prediction(top_k_books):
    """Prepare data for rating prediction
    gets the books that are returned from the content based recommendation
    and prepares it for the rating prediction model
    """
    res = load_data_for_rating_prediction(top_k_books)
    res = xgb_preprocess(res)
    return res # X, y

def calculate_rec_score(rat, cos): 
    """Calculate rec score
    calculates the rec score for each book
    """
    # aggregate cosine sim score snad rating for each book 
    # and rank based on rec score 
    w_sim = 0.2
    w_rating = 0.8
    w_sim = 0.2
    w_rating = 0.8
    return w_sim * cos + w_rating * rat / len()

def get_rating_prediction(data, top_k_books):
    """Get rating prediction
    gets the books that are returned from the content based recommendation
    and predicts the rating for each book
    """
    # get rating prediction
    rating_prediction = xgboost.predict(data)
    # create a df whith sim score and rating prediction
    for book in top_k_books.keys:
        top_k_books[book]['rating_prediction'] = rating_prediction[book]
    df = pd.DataFrame.from_dict(top_k_books, orient='index')
    # calculate rec score
    df['rec_score'] = df.apply(lambda x: calculate_rec_score(x['rating_prediction'], x['cosine_sim']), axis=1)
    ranked_list = df.sort_values(by=['rec_score'], ascending=False)
    return ranked_list
    
def get_top_k_books(user_info):
    """Get top k books
    gets the books that are returned from the content based recommendation
    and predicts the rating for each book
    """
    top_k_books = get_cosine_sim(user_info)
    data = prepare_data_for_rating_prediction(top_k_books)
    ranked_list = get_rating_prediction(data, top_k_books)

    return ranked_list








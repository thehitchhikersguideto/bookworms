# imports
from utils import load_model
from utils import cosine_similarity_content

xgboost = load_model()

# get_top_k_books function



# GET INPUT OF BOOKS


# GET TOP K CONTENT BASED BOOKS


# GET RATINGS OF TOP K 


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
   

    pass

def get_rating_prediction(top_k_books):
    """Get rating prediction
    gets the books that are returned from the content based recommendation
    and predicts the rating for each book
    """

    # aggregate cosine sim score snad rating for each book 
    # and rank based on rec score 
    w_sim = 0.2
    w_rating = 0.8

    rec_score = w_sim * top_k_books['cosine_sim'] + w_rating * top_k_books['rating']

    pass



def get_top_k_books(user_info):
    pass









import pandas as pd
import numpy as np
# Libraries for vectorization of text and one hot encoding, BERT, GPT, RoBERTa
import torch
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import MultiLabelBinarizer
from transformers import BertTokenizer, BertModel, GPT2Tokenizer, GPT2Model, RobertaTokenizer, RobertaModel
from torch.utils.data import DataLoader, Dataset
import ast
import re
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import sys
from pathlib import Path
import json

root_directory = str(Path(__file__).resolve().parents[1])
sys.path.append(root_directory)
from data.datamanager import data_manager



def standardize_publisher_name(publisher):
    # Replace ".com" with an empty string
    publisher = publisher.replace(".com", "")
    
    # Replace 'self-published' and 'self published' with 'self_published'
    publisher = re.sub(r"self[-\s]?published", "self_published", publisher, flags=re.IGNORECASE)

    # Remove all non-alphanumeric characters (except underscores)
    publisher = re.sub(r"[^\w\s]", "", publisher)

    # Convert the publisher name to lowercase
    publisher = publisher.lower()
    
    # Remove leading and trailing whitespaces
    publisher = publisher.strip()
    
    return publisher

def parse_awards(awards_str):
    awards_list = awards_str.strip('][').split(', ')
    return [award.strip() for award in awards_list if award]



def get_recommendations(user_books_ids = ['77203.The_Kite_Runner', '929.Memoirs_of_a_Geisha', '128029.A_Thousand_Splendid_Suns', '19063.The_Book_Thief', '4214.Life_of_Pi'], user_ratings = [4, 4, 3, 5, 4], books_to_return=3):


    data_importer = data_manager.DataImporter(db_name='Processed_Data', collection_name='Embeddings')

    # Get the embeddings from the database
    data_importer.set_pipeline([
        {'$project': {'_id': 0}}
    ])
    embed_data = data_importer.import_data(use_pipeline=True)
    df_embeddings = pd.DataFrame(embed_data)
    available_books = df_embeddings['book_id'].tolist()

    # Get the books from the database
    data_importer.set_db_collection(db_name='Processed_Data', collection_name='processed_books')
    # Only grab the books we have embeddings for and dont grab any columns we dont need
    data_importer.set_pipeline(pipeline = [{"$match": {"book_id": {"$in": available_books}}},{"$project": {"_id": 0,"series": 0,"price": 0,"language": 0,"primary_lists": 0,"year_published": 0, 'description': 0}}])
    book_data = data_importer.import_data(use_pipeline=True)
    df_books = pd.DataFrame(book_data)
    titles_and_ids = df_books[['title', 'book_id', 'author']]
    df_books.drop(columns=['title'], inplace=True)

    # Merge the two dataframes based on the book_id
    df_books_and_embeddings = pd.merge(df_books, df_embeddings, on='book_id')



    df_books_and_embeddings['publisher'] = df_books_and_embeddings['publisher'].apply(standardize_publisher_name)


    min_freq = 10
    # Group less frequent authors into "Others"
    author_counts = df_books_and_embeddings['author'].value_counts()
    authors_to_replace = author_counts[author_counts < min_freq].index
    df_books_and_embeddings['authors_reduced'] = df_books_and_embeddings['author'].replace(authors_to_replace, 'Others')

    # Group less frequent publishers into "Others"
    publisher_counts = df_books_and_embeddings['publisher'].value_counts()
    publishers_to_replace = publisher_counts[publisher_counts < min_freq].index
    df_books_and_embeddings['publisher_reduced'] = df_books_and_embeddings['publisher'].replace(publishers_to_replace, 'Others')

    # One hot encode genres and publishers and author with separate multi label binarizers
    mlb_genres = MultiLabelBinarizer()
    genres = mlb_genres.fit_transform(df_books_and_embeddings['genres'])

    # Create dataframes for each set of one hot encoded features
    genres_df = pd.DataFrame(genres, columns=[f"genre_{c}" for c in mlb_genres.classes_])


    # Reset the index of each one hot encoded dataframe
    df_books_and_embeddings.reset_index(drop=True, inplace=True)
    genres_df.reset_index(drop=True, inplace=True)

    # Concatenate the one hot encoded dataframes with the original dataframe
    df_books_and_embeddings = pd.concat([df_books_and_embeddings, genres_df], axis=1)


    # For the author and publisher a simple one hot encoding will be used
    df_books_and_embeddings_authors_publishers = pd.get_dummies(df_books_and_embeddings, columns=['authors_reduced', 'publisher_reduced'], prefix=['author', 'publisher'])


    # Reset the index of the one hot encoded dataframe
    df_books_and_embeddings_authors_publishers.reset_index(drop=True, inplace=True)

    # Assign the modified dataframe to the original variable
    df_books_and_embeddings = df_books_and_embeddings_authors_publishers


    # Drop the original authors, genres, and publishers columns
    df_books_and_embeddings.drop(columns=['genres', 'author', 'publisher'], inplace=True)

    df_books_and_embeddings['awards'] = df_books_and_embeddings['awards'].astype(str).apply(lambda x: re.sub(r"[^a-zA-Z0-9\s\[\],]", "", x).lower())

    df_books_and_embeddings['awards'] = df_books_and_embeddings['awards'].apply(parse_awards)

    # Get the number of awards for each book
    df_books_and_embeddings = df_books_and_embeddings.reset_index(drop=True)
    df_books_and_embeddings['num_awards'] = df_books_and_embeddings['awards'].apply(lambda x: len(x))
    # Drop the original awards column
    df_books_and_embeddings = df_books_and_embeddings.drop(['awards'], axis=1)


    # Turn all float64 columns into float32
    for col in df_books_and_embeddings.columns:
        if df_books_and_embeddings[col].dtype == 'float64' or df_books_and_embeddings[col].dtype == 'int64' or df_books_and_embeddings[col].dtype == 'int32':
            df_books_and_embeddings[col] = df_books_and_embeddings[col].astype('float32')


    # Remove commas from the number of ratings and reviews
    df_books_and_embeddings['num_ratings'] = df_books_and_embeddings['num_ratings'].apply(lambda x: x.replace(',', ''))
    df_books_and_embeddings['num_reviews'] = df_books_and_embeddings['num_reviews'].apply(lambda x: x.replace(',', ''))
    # Turn the number of ratings and reviews into float32
    df_books_and_embeddings['num_ratings'] = df_books_and_embeddings['num_ratings'].astype('float32')
    df_books_and_embeddings['num_reviews'] = df_books_and_embeddings['num_reviews'].astype('float32')


    # Separate the book_id column
    book_ids = df_books_and_embeddings['book_id']
    numeric_data = df_books_and_embeddings.drop('book_id', axis=1)


    # Truncated SVD for future dimensionality reduction
    """ # Calculate the number of components
    target_ratio = 1/5
    n_components = int(numeric_data.shape[1] * target_ratio)

    # Initialize the TruncatedSVD object
    trunc_svd = TruncatedSVD(n_components=n_components)

    # Fit the TruncatedSVD model and transform your data
    reduced_data = trunc_svd.fit_transform(numeric_data)

    # Convert the reduced data back to a DataFrame
    reduced_data_df = pd.DataFrame(reduced_data)

    # Add the book_id column back to the DataFrame
    reduced_data_df['book_id'] = book_ids.values

    # Reset the index
    reduced_data_df = reduced_data_df.reset_index(drop=True) """

    # Filter the DataFrame to get only the rows corresponding to the books in the user_books_ids list
    user_books_df = df_books_and_embeddings[df_books_and_embeddings['book_id'].isin(user_books_ids)]
    user_books_df['rating'] = user_books_df['rating'].astype('float32')

    # Drop the 'book_id' column and convert the DataFrame to a NumPy array
    user_books_feature_vectors = user_books_df.drop(columns=['book_id']).values

    # If you have user ratings, you can weight the feature vectors by the ratings
    user_books_feature_vectors = user_books_feature_vectors * np.array(user_ratings)[:, np.newaxis]

    print('Non-numeric columns: ')
    print(user_books_df.select_dtypes(exclude=[np.number]))


    user_profile = user_books_feature_vectors.mean(axis=0)
    remaining_books_df = df_books_and_embeddings[~df_books_and_embeddings['book_id'].isin(user_books_ids)]

    remaining_books_feature_vectors = remaining_books_df.drop(columns=['book_id']).values
    """     similarity_scores = cosine_similarity([user_profile], remaining_books_feature_vectors)
    top_indices = np.argsort(similarity_scores[0])[-books_to_return:][::-1]
    recommended_book_ids = remaining_books_df.iloc[top_indices]['book_id'].values """


    similarity_scores = cosine_similarity([user_profile], remaining_books_feature_vectors)

    sorted_indices = np.argsort(similarity_scores[0])[::-1]
    unique_titles = set()
    recommended_book_ids = []


    for ids in sorted_indices:

        current_book_id = remaining_books_df.iloc[ids]['book_id']
        current_title = titles_and_ids[titles_and_ids['book_id'] == current_book_id]['title'].values[0]

        if current_title not in unique_titles:
            recommended_book_ids.append(current_book_id)
            unique_titles.add(current_title)

        if len(recommended_book_ids) == books_to_return:
            break

    recommended_book_ids = np.array(recommended_book_ids)

    # Get the book titles and authors for the recommended books, store as json of dicionary of {{book_id:x, title:y, author:z}}, {...}}
    recommended_books = []
    for book_id in recommended_book_ids:
        recommended_books.append({'book_id': book_id, 'title': titles_and_ids[titles_and_ids['book_id'] == book_id]['title'].values[0], 'author': titles_and_ids[titles_and_ids['book_id'] == book_id]['author'].values[0]})
    recommended_books = json.dumps(recommended_books)
    print("Recommended books:", recommended_books)
    return recommended_books

if __name__ == '__main__':
    get_recommendations()
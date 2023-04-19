""" Pre-Process Data for XGBoost """

import re
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.decomposition import PCA
from glove_embeddings import embeddings
from load_data import load_data

# CLEAN SERIES

def preprocess_series(df_proc):
    df_proc['series'] = df_proc['series'].apply(lambda x: 1 if x != None else 0)
    return df_proc

# CLEAN TEXT
def remove_stopwords(sen, stop_words):
    sen_new = " ".join([i for i in sen if i not in stop_words])
    return sen_new

def preprocess_title_and_description(df_proc, stop_words):
    df_proc['cleaned_title'] = df_proc['title'].apply(lambda x: x.lower())
    df_proc['cleaned_title'] = df_proc['cleaned_title'].apply(lambda x: re.sub('[^A-Za-z0-9]+', ' ', x))
    df_proc['cleaned_title'] = [remove_stopwords(r.split(), stop_words) for r in df_proc['cleaned_title']]
    df_proc.drop(columns=['title'], inplace=True)
    df_proc['cleaned_description'] = df_proc['description'].apply(lambda x: x.lower())
    df_proc['cleaned_description'] = df_proc['cleaned_description'].apply(lambda x: re.sub('[^A-Za-z0-9]+', ' ', x))
    df_proc['cleaned_description'] = [remove_stopwords(r.split(), stop_words) for r in df_proc['cleaned_description']]
    df_proc.drop(columns=['description'], inplace=True)
    return df_proc

# CLEAN DICIONARIES

get_key_values_from_list = lambda x: [i['k'] for i in x] if len(x) > 0 else []
get_key_values_from_list_nans = lambda x: [i['k'] for i in x] if x !=None else []

def generator_format_list_of_dicts(df, keys):
    """
    Generator function to format the list of dictionaries in the column 'key'
    """
    for key in keys: 
        # apply
        # if value is none then skip
        # if it throws an error then print out the error and skip
        try:
            if key == 'primary_lists':
                df[key] = df[key].apply(get_key_values_from_list_nans)
            else: 
                df[key] = df[key].apply(get_key_values_from_list)
        except Exception as e:
            # print more info about the error
            print('Error in generator_format_list_of_dicts')
            
            print(e)
            continue
    return df

def clean_genres_column(df_proc):
    """ clean the genres column"""
    df_proc['genres'] = df_proc['genres'].apply(lambda x: [i.lower().replace(' ', '').replace('.', '') for i in x])
    # if there are no genres then add a 'none' genre
    df_proc['genres'] = df_proc['genres'].apply(lambda x: ['none'] if len(x) == 0 else x)
    return df_proc
    
# CLEAN NUMBERS

def string_to_float_generator(x): 
    if x == 'None':
        return 0 
    elif type(x) == float:
        return x
    elif 'm' in x:
        return float(x.replace('m', '').replace(',', '')) * 1000000
    elif 'k' in x:
        return float(x.replace('k', '').replace(',', '')) * 1000
    else:
        return 0 
    
def preprocess_numbers(df_proc):
    w_ratings = 0.5
    w_current_readers = 0.25
    w_wanted_to_read = 0.25
    w_reviews = 0.25
    w_num_ratings = 0.25
    keys = ['current_readers', 'wanted_to_read']

    # we have the number of current readers, and the number of people who want to read the book
    # we can actually use this to create a popularity metric
    df_proc['current_readers'] = df_proc['current_readers'].apply(lambda x: string_to_float_generator(x) if x != None else -1)
    df_proc['wanted_to_read'] = df_proc['wanted_to_read'].apply(lambda x: string_to_float_generator(x) if x != None else -1)
    # change the string numners to float numbers
    df_proc['num_reviews'] = df_proc['num_reviews'].apply(lambda x: float(x.replace(',', '')) if x != None else 0)
    df_proc['num_ratings'] = df_proc['num_ratings'].apply(lambda x: float(x.replace(',', '')) if x != None else 0)
    df_proc['rating'] = df_proc['rating'].apply(lambda x: float(x) if x != None else 0)
    # check the dtypes  of current_readers	wanted_to_read	num_reviews	num_ratings	rating
    features = ['current_readers', 'wanted_to_read', 'num_reviews', 'num_ratings', 'rating']

    df_proc['price'] = df_proc['price'].apply(lambda x: float(x.replace('$', '')) if x != None else 0)
    # fill price by average price if it is missing 
    df_proc['price'] = df_proc['price'].apply(lambda x: df_proc['price'].mean() if x == 0 else x)

    # first convert strings to numbers and then replace nan with average based on the genre
    df_proc['price'] = df_proc['price'].apply(lambda x: float(x) if x != None else np.nan)

    # get the average price for each genre
    # df_proc['price'] = df_proc['price'].fillna(df_proc['price'].mean())

    # get the average price for each genre
    df_proc['price'] = df_proc.groupby('publisher')['price'].transform(lambda x: x.fillna(x.mean()))


    # lets create a popularit metric using the ratings, current readers, and wanted to read, and the number of reviews and standardize it
    # Standardized Popularity = (Popularity - μ) / σ

    df_proc['popularity'] = (w_ratings * df_proc['rating'] + w_current_readers * df_proc['current_readers'] + w_wanted_to_read * df_proc['wanted_to_read'] + w_reviews * df_proc['num_reviews'] + w_num_ratings * df_proc['num_ratings']) / (w_ratings + w_current_readers + w_wanted_to_read + w_reviews + w_num_ratings)

    return  df_proc


# DEAL WITH LANGUAGES

def clean_language_column(df_proc):
    # check if the book titles are in english if not drop them
    # if the book title is asccii then we assume it is in english  and we fill the na with english 
    df_proc['language'] = df_proc['language'].apply(lambda x: 'English' if x == None else x)
    # drop everything except english
    df_proc = df_proc[df_proc['language'] == 'English']
    df_proc.drop(columns=['language'], inplace=True)
    return df_proc

def clean_year_published_column(df_proc):
    df_proc.drop(columns=['year_published'], inplace=True)
    return df_proc



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


def clean_cats(df_proc):
    publisher_counts = df_proc['publisher'].value_counts()
    author_counts = df_proc['author'].value_counts()
    publishers_to_replace = publisher_counts[publisher_counts < 10].index
    authors_to_replace = author_counts[author_counts < 10].index

    df_proc['publisher'] = df_proc['publisher'].replace(publishers_to_replace, 'Others')
    df_proc['author'] = df_proc['author'].replace(authors_to_replace, 'Others')

    return df_proc

def multi_label_bin(df_eng, mlb): 
    # change the array of the genres into a string
    df_eng['genres'] = df_eng['genres'].apply(lambda x: str(x))

    # split the genres into a list
    df_eng['genres'] = df_eng['genres'].apply(lambda x: x.split(','))
    df_eng['genres'].head()

    # one hot encode the genres
    df_eng = df_eng.join(pd.DataFrame(mlb.fit_transform(df_eng.pop('genres')),
                                columns=mlb.classes_,
                                index=df_eng.index))


    
    df_eng.columns = df_eng.columns.str.replace("[\[\]']", '', regex=True)

    return df_eng

def clean_other_cats(df_eng): 
    df_eng['awards'] = df_eng['awards'].apply(lambda x: len(x) if x != None else 0)
    df_eng = pd.get_dummies(df_eng, columns=['author', 'publisher'], drop_first=True)
    df_eng = df_eng.apply(lambda x: x.astype(int) if x.dtype == 'bool' else x)
    return df_eng

def vectorization_gen(x):
    if len(x) != 0:
        v = sum([embeddings.get(w, np.zeros((100,))) for w in x.split()])/(len(x.split())+0.001)
        yield v
    else:
        v = np.zeros((100,))
        yield v
    

def get_embeddings(df_emb, emb_path): 
    df_emb = df_emb.loc[:,~df_emb.columns.duplicated()]
    df_emb['emb_description'] = df_emb['cleaned_description'].apply(lambda x: next(vectorization_gen(x)))
    df_emb['emb_title'] = df_emb['cleaned_title'].apply(lambda x: next(vectorization_gen(x)))
    # drop cleaned description and title
    df_emb.drop(columns=['cleaned_description', 'cleaned_title'], inplace=True)

    return df_emb


def perform_pca(df_emb, pca): 
    description_embeddings = df_emb['emb_description'].tolist()

    # Apply PCA to reduce dimensionality of the embeddings
    reduced_embeddings = pca.fit_transform(description_embeddings)

    # Convert the reduced embeddings back into a DataFrame
    reduced_embeddings_df = pd.DataFrame(reduced_embeddings, columns=[f'pca_{i+1}' for i in range(reduced_embeddings.shape[1])])

    # Merge the reduced embeddings DataFrame back with your original dataset
    data_with_reduced_embeddings = pd.concat([df_emb.reset_index(drop=True), reduced_embeddings_df.reset_index(drop=True)], axis=1)

    return data_with_reduced_embeddings

def final_stage(df_fin): 
    df_fin.drop(columns=['emb_description', 'emb_title'], inplace=True)
    # split data into X and y
    y = df_fin['rating']
    X = df_fin.drop(columns=['rating'], axis=1)
    return X, y


def pre_process_data(df, emb_path): 
    # variables
    stop_words = stopwords.words('english')
    mlb = MultiLabelBinarizer()
    pca = PCA(n_components=100)
    # clean the data
    df = preprocess_series(df)
    df = clean_language_column(df)
    df = clean_year_published_column(df)
    df = clean_cats(df)
    df = multi_label_bin(df, mlb)
    df = clean_other_cats(df)
    df = get_embeddings(df, emb_path)
    df = perform_pca(df, pca)
    X, y = final_stage(df)
    return X, y


def get_data_for_xgboost():
    data = load_data()
    X, y = pre_process_data(data, 'glove.6B.100d.txt')
    return X, y


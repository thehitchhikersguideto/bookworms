#!/usr/bin/env python
# coding: utf-8

# In[38]:


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


# Import dataset
df1 = pd.read_csv('processed_books.csv')

# Drop some columns
df1 = df1.drop(['series','price', 'language', 'primary_lists'], axis=1)

# Strip book_id column
df1['book_id'] = df1['book_id'].str.strip()

# Get duplicate count in book_id column
df1.drop_duplicates(subset=['book_id'], inplace=True)

# Drop rows with missing values
df1 = df1.dropna()


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)


class TextDataset(Dataset):
    def __init__(self, texts, tokenizer, max_length=512):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        input_ids = self.tokenizer.encode(self.texts[idx], add_special_tokens=True, max_length=self.max_length, truncation=True)
        return torch.tensor(input_ids)



def get_embeddings(texts, tokenizer, model, batch_size=8):
    dataset = TextDataset(texts, tokenizer)
    loader = DataLoader(dataset, batch_size=batch_size, collate_fn=lambda x: torch.nn.utils.rnn.pad_sequence(x, batch_first=True))

    embeddings = []
    with torch.no_grad():
        for batch in loader:
            batch = batch.to(device)
            outputs = model(batch)
            batch_embeddings = outputs[0].mean(dim=1).cpu().numpy()
            embeddings.extend(batch_embeddings)
    return embeddings



# BERT
bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased').to(device)
title_bert = get_embeddings(df1['title'].tolist(), bert_tokenizer, bert_model)
description_bert = get_embeddings(df1['description'].tolist(), bert_tokenizer, bert_model)

del bert_model
torch.cuda.empty_cache()

# GPT-2
gpt_tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
gpt_model = GPT2Model.from_pretrained('gpt2').to(device)
title_gpt = get_embeddings(df1['title'].tolist(), gpt_tokenizer, gpt_model)
description_gpt = get_embeddings(df1['description'].tolist(), gpt_tokenizer, gpt_model)

del gpt_model
torch.cuda.empty_cache()

# RoBERTa
roberta_tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
roberta_model = RobertaModel.from_pretrained('roberta-base').to(device)
title_roberta = get_embeddings(df1['title'].tolist(), roberta_tokenizer, roberta_model)
description_roberta = get_embeddings(df1['description'].tolist(), roberta_tokenizer, roberta_model)

del roberta_model
torch.cuda.empty_cache()



# Create dataframes for each set of embeddings
title_bert_df = pd.DataFrame(title_bert, columns=[f"title_bert_{i}" for i in range(len(title_bert[0]))])
description_bert_df = pd.DataFrame(description_bert, columns=[f"description_bert_{i}" for i in range(len(description_bert[0]))])

title_gpt_df = pd.DataFrame(title_gpt, columns=[f"title_gpt_{i}" for i in range(len(title_gpt[0]))])
description_gpt_df = pd.DataFrame(description_gpt, columns=[f"description_gpt_{i}" for i in range(len(description_gpt[0]))])

title_roberta_df = pd.DataFrame(title_roberta, columns=[f"title_roberta_{i}" for i in range(len(title_roberta[0]))])
description_roberta_df = pd.DataFrame(description_roberta, columns=[f"description_roberta_{i}" for i in range(len(description_roberta[0]))])

# Reset the index of the original dataframe
df1.reset_index(drop=True, inplace=True)

# Reset the index of each embeddings dataframe
title_bert_df.reset_index(drop=True, inplace=True)
description_bert_df.reset_index(drop=True, inplace=True)
title_gpt_df.reset_index(drop=True, inplace=True)
description_gpt_df.reset_index(drop=True, inplace=True)
title_roberta_df.reset_index(drop=True, inplace=True)
description_roberta_df.reset_index(drop=True, inplace=True)

# Concatenate the embeddings dataframes with the original dataframe
df_text_desc_embeds = pd.concat([df1, title_bert_df, description_bert_df, title_gpt_df, description_gpt_df, title_roberta_df, description_roberta_df], axis=1)


df_text_desc_embeds = df_text_desc_embeds.drop(['title', 'description', 'year_published'], axis=1)

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

# Apply the function to the publisher column
df_text_desc_embeds['publisher'] = df_text_desc_embeds['publisher'].apply(standardize_publisher_name)

min_freq = 10
# Group less frequent authors into "Others"
author_counts = df_text_desc_embeds['author'].value_counts()
authors_to_replace = author_counts[author_counts < min_freq].index
df_text_desc_embeds['authors_reduced'] = df_text_desc_embeds['author'].replace(authors_to_replace, 'Others')

# Group less frequent publishers into "Others"
publisher_counts = df_text_desc_embeds['publisher'].value_counts()
publishers_to_replace = publisher_counts[publisher_counts < min_freq].index
df_text_desc_embeds['publisher_reduced'] = df_text_desc_embeds['publisher'].replace(publishers_to_replace, 'Others')


duplicate_columns = df_text_desc_embeds.columns.duplicated().sum()

# Print the number of duplicate column names
print(f"Number of duplicate column names: {duplicate_columns}")

# Show the shape of the dataframe
print(f"Shape of the dataframe: {df_text_desc_embeds.shape}")


# Apply ast.literal_eval() using a lambda operation to the 'awards' column
df_text_desc_embeds['genres'] = df_text_desc_embeds['genres'].apply(lambda x: ast.literal_eval(x))

# One hot encode genres and publishers and author with separate multi label binarizers
mlb_genres = MultiLabelBinarizer()
genres = mlb_genres.fit_transform(df_text_desc_embeds['genres'])


# Create dataframes for each set of one hot encoded features
genres_df = pd.DataFrame(genres, columns=[f"genre_{c}" for c in mlb_genres.classes_])



df_text_desc_embeds.reset_index(drop=True, inplace=True)
genres_df.reset_index(drop=True, inplace=True)
df_text_desc_embeds = pd.concat([df_text_desc_embeds, genres_df], axis=1)
df_text_desc_embeds_authors_publishers = pd.get_dummies(df_text_desc_embeds, columns=['authors_reduced', 'publisher_reduced'], prefix=['author', 'publisher'])

df_text_desc_embeds_authors_publishers.reset_index(drop=True, inplace=True)
df_text_desc_embeds = df_text_desc_embeds_authors_publishers


df_text_desc_embeds.drop(columns=['genres', 'author', 'publisher'], inplace=True)

# For every entry in the 'awards' column only use alphanumeric characters and '[]' and ',' and convert to lowercase
df_text_desc_embeds['awards'] = df_text_desc_embeds['awards'].astype(str).apply(lambda x: re.sub(r"[^a-zA-Z0-9\s\[\],]", "", x).lower())

def parse_awards(awards_str):
    awards_list = awards_str.strip('][').split(', ')
    return [award.strip() for award in awards_list if award]

df_text_desc_embeds['awards'] = df_text_desc_embeds['awards'].apply(parse_awards)

# Get the number of awards for each book
df_text_desc_embeds = df_text_desc_embeds.reset_index(drop=True)
df_text_desc_embeds['num_awards'] = df_text_desc_embeds['awards'].apply(lambda x: len(x))
# Drop the original awards column
df_text_desc_embeds = df_text_desc_embeds.drop(['awards'], axis=1)




# Turn all float64 columns into float32
for col in df_text_desc_embeds.columns:
    if df_text_desc_embeds[col].dtype == 'float64' or df_text_desc_embeds[col].dtype == 'int64' or df_text_desc_embeds[col].dtype == 'int32':
        df_text_desc_embeds[col] = df_text_desc_embeds[col].astype('float32')

# Remove commas from the number of ratings and reviews
df_text_desc_embeds['num_ratings'] = df_text_desc_embeds['num_ratings'].apply(lambda x: x.replace(',', ''))
df_text_desc_embeds['num_reviews'] = df_text_desc_embeds['num_reviews'].apply(lambda x: x.replace(',', ''))
# Turn the number of ratings and reviews into float32
df_text_desc_embeds['num_ratings'] = df_text_desc_embeds['num_ratings'].astype('float32')
df_text_desc_embeds['num_reviews'] = df_text_desc_embeds['num_reviews'].astype('float32')


# Separate the book_id column
book_ids = df_text_desc_embeds['book_id']
numeric_data = df_text_desc_embeds.drop('book_id', axis=1)

# Calculate the number of components
target_ratio = 1/5
n_components = int(numeric_data.shape[1] * target_ratio)


trunc_svd = TruncatedSVD(n_components=n_components)

reduced_data = trunc_svd.fit_transform(numeric_data)

reduced_data_df = pd.DataFrame(reduced_data)

# Add the book_id column back to the DataFrame
reduced_data_df['book_id'] = book_ids.values

# Reset the index
reduced_data_df = reduced_data_df.reset_index(drop=True)

user_books_ids = ['77203.The_Kite_Runner', '929.Memoirs_of_a_Geisha', '128029.A_Thousand_Splendid_Suns', '19063.The_Book_Thief', '4214.Life_of_Pi']
user_ratings = [4, 4, 3, 5, 4]

# Filter the DataFrame to get only the rows corresponding to the books in the user_books_ids list
user_books_df = df_text_desc_embeds[df_text_desc_embeds['book_id'].isin(user_books_ids)]

# Drop the 'book_id' column and convert the DataFrame to a NumPy array
user_books_feature_vectors = user_books_df.drop(columns=['book_id']).values

# If you have user ratings, you can weight the feature vectors by the ratings
user_books_feature_vectors = user_books_feature_vectors * np.array(user_ratings)[:, np.newaxis]

user_profile = user_books_feature_vectors.mean(axis=0)

remaining_books_df = df_text_desc_embeds[~df_text_desc_embeds['book_id'].isin(user_books_ids)]

# Drop the 'book_id' column and convert the remaining books DataFrame to a NumPy array
remaining_books_feature_vectors = remaining_books_df.drop(columns=['book_id']).values

# Calculate similarity scores between the user profile and the remaining books
similarity_scores = cosine_similarity([user_profile], remaining_books_feature_vectors)

# Get the indices of the top N most similar books
N = 10
top_indices = np.argsort(similarity_scores[0])[-N:][::-1]

# Get the top N most similar books' book_ids
recommended_book_ids = remaining_books_df.iloc[top_indices]['book_id'].values

print("Recommended books:", recommended_book_ids)


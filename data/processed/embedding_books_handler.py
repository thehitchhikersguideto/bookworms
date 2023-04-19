# This file is used to process and push the title and description embeddings to the database. The embeddings are used to calculate the similarity between books.
# Updating the embeddings in mongodb will require that we pull all the books from the database, process them, and then push them back to the embeddings database, this is computationally expensive but necessary to make sure updated data has the 
# same dimensionality as the old data. This should of course be done sparingly, and only when the data has changed significantly.
import pandas as pd
# Libraries for vectorization of text and one hot encoding, BERT, GPT, RoBERTa
import torch
from transformers import BertTokenizer, BertModel, GPT2Tokenizer, GPT2Model, RobertaTokenizer, RobertaModel
from torch.utils.data import DataLoader, Dataset
import data_manager


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

def preprocessing(df):
    df['book_id'] = df['book_id'].str.strip()
    # Get duplicate count in book_id column
    df.drop_duplicates(subset=['book_id'], inplace=True)
    # Drop rows with missing values
    df = df.dropna()
    return df

data_importer = data_manager.DataImporter()
data_exporter = data_manager.DataExporter()
data_exporter.set_db_collection(db_name = 'Processed_Data', collection_name = 'Embeddings')
data_importer.set_db_collection(db_name = 'Processed_Data', collection_name = 'processed_books')
# Dont grab the _id field
data_importer.set_pipeline([
    {'$project': {'_id': 0, 'series': 0, 'price': 0, 'language': 0, 'primary_lists': 0, 'year_published': 0}}
])

data = data_importer.import_data(use_pipeline=True)
df1 = pd.DataFrame(data)
df1 = preprocessing(df1)
book_id_df = df1['book_id']
print(df1.columns)
print(df1.head(1))

# Option to use BERT, GPT, or RoBERTa
""" # BERT
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
torch.cuda.empty_cache() """

# RoBERTa
roberta_tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
roberta_model = RobertaModel.from_pretrained('roberta-base').to(device)
title_roberta = get_embeddings(df1['title'].tolist(), roberta_tokenizer, roberta_model)
description_roberta = get_embeddings(df1['description'].tolist(), roberta_tokenizer, roberta_model)

del roberta_model
torch.cuda.empty_cache() 


 

# Create dataframes for each set of embeddings
""" title_bert_df = pd.DataFrame(title_bert, columns=[f"title_bert_{i}" for i in range(len(title_bert[0]))])
description_bert_df = pd.DataFrame(description_bert, columns=[f"description_bert_{i}" for i in range(len(description_bert[0]))])

title_gpt_df = pd.DataFrame(title_gpt, columns=[f"title_gpt_{i}" for i in range(len(title_gpt[0]))])
description_gpt_df = pd.DataFrame(description_gpt, columns=[f"description_gpt_{i}" for i in range(len(description_gpt[0]))]) """

title_roberta_df = pd.DataFrame(title_roberta, columns=[f"title_roberta_{i}" for i in range(len(title_roberta[0]))])
description_roberta_df = pd.DataFrame(description_roberta, columns=[f"description_roberta_{i}" for i in range(len(description_roberta[0]))]) 

# Reset the index of the original dataframe
df1.reset_index(drop=True, inplace=True)

# Reset the index of each embeddings dataframe
""" title_bert_df.reset_index(drop=True, inplace=True)
description_bert_df.reset_index(drop=True, inplace=True)
title_gpt_df.reset_index(drop=True, inplace=True)
description_gpt_df.reset_index(drop=True, inplace=True) """
title_roberta_df.reset_index(drop=True, inplace=True)
description_roberta_df.reset_index(drop=True, inplace=True) 
book_id_df.reset_index(drop=True, inplace=True)

# Concatenate the embeddings dataframes with the original dataframe
df_text_desc_embeds = pd.concat([book_id_df, title_roberta_df, description_roberta_df], axis=1) # title_gpt_df, description_gpt_df,  title_bert_df, description_bert_df\

# Debug analytics
""" # Print the length of each dataframe
print("Length of book_id_df:", len(book_id_df))
print("Length of title_roberta_df:", len(title_roberta_df))
print("Length of description_roberta_df:", len(description_roberta_df))

# Print the number of duplicates in the book_id_df
print("Number of duplicates in book_id_df:", book_id_df.duplicated().sum())

# Print the number of nans in the book_id column
print(df_text_desc_embeds['book_id'].isna().sum())
# Print total number of of rows who contain nans
print(df_text_desc_embeds.isna().sum().sum())

mask = df_text_desc_embeds.drop(columns=['book_id']).isna().any(axis=1)

# count the number of rows where NaNs are present in the masked columns
num_rows_with_nans = mask.sum()
print(num_rows_with_nans) """

# Export the dataframe to MongoDB
print('Exporting data to MongoDB...')
data = df_text_desc_embeds.to_dict('records')
print(data[0])
data_exporter.export_data(data) 
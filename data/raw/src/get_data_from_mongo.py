
# imports
import os
import sys
import pandas as pd
from config import get_mongo_config
import pymongo
from typing import Collection, Tensor
import tensorflow as tf




def get_data_from_mongo(cfg) -> Collection:
    
    client = pymongo.MongoClient(cfg.mongo_uri):
    db = client[cfg.mongo_db]
    col = db[cfg.mongo_col]
    cursor = col.find()
    for rec in cursor: 
        yield rec
    
# requires testing 
def get_tensors_from_mongo(cfg) -> Tensor: 
    # using the get_data_from_mongo function, get the data from mongo with generators
    tf_data = tf.data.Dataset.from_generator(
        get_data_from_mongo,
        output_types = tf.float32,
        output_shapes = tf.TensorShape([None])
    )
    return tf_data



def main(): 
    # get the config
    cfg = get_mongo_config()

    # get the data
    data = get_data_from_mongo(cfg)

    
    




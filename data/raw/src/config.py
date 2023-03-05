import os 
import sys
from dataclasses import dataclass


@dataclass
class MongoConfig:
    mongo_uri = os.environ['MONGO_URI']
    mongo_db = os.environ['MONGO_DB']
    mongo_col = os.environ['MONGO_COL']
    mongo_dest = os.environ['MONGO_DEST']




def get_mongo_config(): 
    # generate a dictionary of the mongo config
    config = MongoConfig()
    mongo_config = {
        'uri': config.mongo_uri,
        'db': config.mongo_db,
        'col': config.mongo_col,
        'dest': config.mongo_dest
    }

    # ensure that noneo of the config values are empty
    for key, value in mongo_config.items():
        if value == '':
            ValueError(f'The {key} environment variable cannot be empty.')
    
    return mongo_config






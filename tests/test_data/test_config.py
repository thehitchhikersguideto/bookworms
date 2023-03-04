import pymongo 
import pytest
from data import get_mongo_config
# write the tests

# tests
def test_config():
    env = {
        'MONGO_URI': 'mongodb://localhost:27017',
        'MONGO_DB': 'test',
        'MONGO_COL': 'test',
        'MONGO_DEST': 'test'
    }
    false_env = {
        'MONGO_URI': '',
        'MONGO_DB': '',
        'MONGO_COL': '',
        'MONGO_DEST': ''
    }


    assert get_mongo_config(env) == {
        'uri': 'mongodb://localhost:27017',
        'db': 'test',
        'col': 'test',
        'dest': 'test'
    }
    with pytest.raises(ValueError):
        get_mongo_config(false_env)
        


    

    
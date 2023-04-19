"""Load model from pickle file."""

import pickle

def load_model(model_path='recommender/utils/xgb_model.pkl'):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model




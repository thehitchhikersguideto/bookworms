"""
TF Model Class for a combined recommendation model

"""

import tensorflow as tf
from tensorflow import keras
import tensorflow_recommenders as tfrs
from QueryModel import QueryModel
from ExerciseModel import ExerciseModel

class RecoModel(tf.keras.Model):
    def __init__(self, layer_sizes):
        super().__init__()

        self.query_model = QueryModel(layer_sizes)
        self.exercise_model = ExerciseModel(layer_sizes)

        self.task = tfrs.tasks.Retrieval(
            metrics - tfrs.metrics.FactorizedTopK(
            candidates=exercises.batch(128).map(self.exercise_model), 
            ), 
        )

    def compute_loss(self, features, training = False): 
        query_embeddings = self.query_model({
            'bucketized_age': features['bucketized_age'],
            'user_gender': features['user_gender']
        })

        exercise_embeddings = self.exercise_model({
            features['exercise_name']
        })

        return self.task(query_embeddings, exercise_embeddings, compute_metrics = not training)
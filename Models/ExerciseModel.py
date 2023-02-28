"""
TF Model Class for a single exercise entity acting as a candidate in the recommendation system
"""

import tensorflow as tf
from ExercisesModel import ExercisesModel

class ExerciseModel(tf.keras.Model):
    def __init__(self, layer_sizes):
        super.__init__()

        self.embedding_model = ExercisesModel()

        self.dense_layers = tf.keras.Sequential()

        for l in layer_sizes[:-1]:
            self.dense_layers.add(tf.keras.layers.Dense(l, activation='relu'))

        for l in layer_sizes[-1:]:
            self.dense_layers.add(tf.keras.layers.Dense(l))
        
    def call(self, inputs):
        feature_embeddings = self.embedding_model(inputs)
        return self.dense_layers(feature_embeddings)
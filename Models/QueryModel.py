"""
TF Model for encoding the user queries

"""
import tensorflow as tf
from UserModel import UserModel


class QueryModel(tf.keras.Model):

    def __init__(self, layer_sizes):
        """
        Args:
            layer_sizes: A list of integers representing the size of each layer
        """
        super().__init__()

        #Generate user model embeddings

        self.embedding_model = UserModel()

        self.dense_layers = tf.keras.Sequential()

        #Activation function = ReLU
        for l in layer_sizes[:-1]:
            self.dense_layers.add(tf.keras.layers.Dense(l, activation='relu'))

        #Output layer
        for l in layer_sizes[-1:]:
            self.dense_layers.add(tf.keras.layers.Dense(l))

    def call(self,inputs):
        feature_embeddings = self.embedding_model(inputs)
        return self.dense_layers(feature_embeddings)
    
        





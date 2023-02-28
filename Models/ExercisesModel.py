"""
Model for encoding the exercises 
"""
import tensorflow as tf

class ExercisesModel(tf.keras.Model):

    def __init__(self):
        super().__init__()

        max_tokens = 1500

        self.exercise_embedding = tf.keras.Sequential([
            tf.keras.layers.StringLookup(vocabulary=unique_exercise_names, mask_token=None),
            tf.keras.layers.Embedding(len(unique_exercise_names) + 1, 32)
        ])
        

        self.exercise_vectorizer = tf.keras.layers.TextVectorization(
            max_tokens=max_tokens
        )

        self.exercise_desc_embedding = tf.keras.Sequential([
            self.exercise_vectorizer,
            tf.keras.layers.Embedding(max_tokens, 32, mask_zero=True),
            tf.leras.layers.GlobalAveragePooling1D()
        ])  

        self.exercise_vectorizer.adapt(exercises)

        def call(self, exercise_names): 
            return tf.concat([
                self.exercise_embedding(exercise_names),
                self.exercise_desc_embedding(exercise_names)

            ], axis=1)
            

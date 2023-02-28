import tensorflow as tf


class UserModel(tf.keras.Model):
    def __init__(self):
        super().__init__()

        self.age_embedding = tf.keras.Sequential([
            tf.keras.layers.IntegerLookup(vocabulary=unique_bucketized_ages, mask_token=None),
            tf.keras.layers.Embedding(len(unique_bucketized_ages) + 1, 32)
        ])

        self.gender_embedding = tf.keras.Sequential([
            tf.keras.layers.IntegerLookup(vocabulary=unique_user_gender, mask_token=None),
            tf.keras.layers.Embedding(len(unique_user_gender) + 1, 32)
    ])
        
    def call(self, inputs): 
        return tf.concat([
            self.age_embedding(inputs['bucketized_age']),
            self.gender_embedding(inputs['user_gender'])
        ], axis=1)
    

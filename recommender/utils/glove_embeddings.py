"""GloVe embeddings."""

import numpy as np


def embeddings(path):
    word_embeddings = {}
    
    f = open(path, encoding='utf-8')
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        word_embeddings[word] = coefs
    f.close()

    return word_embeddings


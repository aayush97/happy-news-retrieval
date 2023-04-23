import pandas as pd
import numpy as np
from scripts.doc2vector import text2vec
import os
from numpy.linalg import norm


def get_random_tweets(df, n):
    return df.sample(n)


def get_random_tweet(n=100):
    df = pd.read_csv(os.path.join(os.getcwd(), 'data/good_tweets.csv'))
    df = df.sample(n)
    return df['Tweet'].tolist()


def get_mean_tweet_vector(tweets):
    vectors = [text2vec(tweet) for tweet in tweets]
    return np.mean(vectors, axis=0)


def get_initial_user_vector():
    tweets = get_random_tweet()
    return get_mean_tweet_vector(tweets)


def update_user_vector_naive(user_vector, tweet):
    tweet_vector = text2vec(tweet)
    new_user_vector = (user_vector + tweet_vector) / 2
    return new_user_vector


def update_user_vector_adaptive(user_vector, tweet, count):
    tweet_vector = text2vec(tweet)
    new_user_vector = user_vector + (tweet_vector-user_vector) / (count + 1)
    return new_user_vector


def update_user_vector_cosine_similarity(user_vector, tweet, clicked=1, step_size=0.5, reg=0.1):
    tweet_vector = text2vec(tweet)
    new_user_vector = user_vector - step_size * \
        ((np.dot(user_vector.squeeze(), tweet_vector.squeeze()) - clicked)
         * tweet_vector + reg*user_vector)
    return new_user_vector

def get_similarity_between_user_doc_vectors(user_vector, document):
    doc_vector = text2vec(document)
    score = np.dot(user_vector, doc_vector.T) / (norm(user_vector) * norm(doc_vector))
    return score[0]
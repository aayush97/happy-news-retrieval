import tweepy
import json
import pandas as pd
import numpy as np
import os

# Set the path to your credentials JSON file:
credentials = "twitter_creds.json"
with open(credentials, "r") as keys:
    api_tokens = json.load(keys)


API_KEY = api_tokens["api_key"]
API_SECRET = api_tokens["api_secret"]
BEARER_TOKEN = api_tokens["bearer_token"]
ACCESS_TOKEN = api_tokens["access_token"]
ACCESS_SECRET = api_tokens["access_secret"]


# auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
# auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
auth = tweepy.OAuth2BearerHandler(BEARER_TOKEN)
api = tweepy.API(auth)


# Function to extract tweets
def get_tweets(query, limit=100, type="mixed"):

    happy_terms = ["happy", "win", "heartwarming", "positive", "inspiring", "feel-good", "uplifting", "positive", "cute", "adorable", ]
    negative_terms = ["loss", "lose", "negative", "sad"]
    if query == 'Any':
        query = ""

    expanded_query = "(" + " OR ".join(happy_terms) + ") -(" + " OR ".join(negative_terms) + ") -filter:retweets " + query 
    tweets = tweepy.Cursor(api.search_tweets,
                           q=expanded_query,
                           tweet_mode='extended',
                           result_type=type,
                           include_entities=True,
                           lang='en').items(limit)

    columns = ['id', 'tweet', 'length', 'query', 'url', 'entities_url', 'time',
               'screen_name', 'favorite_count', 'retweet_count']
    data = []

    # Iterate through the results and append them to the list
    for tweet in tweets:
        url = "https://twitter.com/twitter/status/" + str(tweet.id)
        if len(tweet.entities['urls']):
             entities_url = tweet.entities['urls'][0]['url']
        else:
             entities_url = ""     
             
        data.append([tweet.id, tweet.full_text,
                     len(tweet.full_text), query, url, entities_url, tweet.created_at,
                     tweet.user.screen_name, tweet.favorite_count,
                     tweet.retweet_count])        

    # Create a dataframe with the results
    df = pd.DataFrame(data, columns=columns)
    filename = os.path.join(os.getcwd(), 'data/tweets_for_query.csv')

    if os.path.exists(filename):
        df.to_csv(filename, mode='a', index=False, header=False)

    else:
        df.to_csv(filename, mode='w', index=False, header=True)

    return data


def get_tweets_user(user, query, limit=5000):

    tweets = tweepy.Cursor(api.user_timeline,
                           screen_name=user,
                           tweet_mode='extended',
                           exclude_replies=True,
                           include_rts=False).items(limit)

    columns = ['id', 'Tweet', 'length', 'url', 'entity_url', 'Time',
               'screen_name', 'favorite_count', 'retweet_count']
    data = []

    # Iterate through the results and append them to the list
    for tweet in tweets:
        url = "https://twitter.com/twitter/status/" + str(tweet.id) 
        if len(tweet.entities['urls']):
             entities_url = tweet.entities['urls'][0]['url']
        else:
             entities_url = "" 

        data.append([tweet.id, tweet.full_text,
                     len(tweet.full_text), url, entities_url, tweet.created_at,
                     tweet.user.screen_name, tweet.favorite_count,
                     tweet.retweet_count])

    # Create a dataframe with the results
    df = pd.DataFrame(data, columns=columns)

    filename = os.path.join(os.getcwd(), 'data/good_tweets.csv')

    if os.path.exists(filename):
        df.to_csv(filename, mode='a', index=False, header=False)

    else:
        df.to_csv(filename, mode='w', index=False, header=True)

    return data


# Driver code
if __name__ == '__main__':
    get_tweets("football")
    # get_tweets_user("goodnewsnetwork", "#covid19")

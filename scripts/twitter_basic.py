import json
import tweepy
import sys
import csv
import os
import pandas as pd
import numpy as np

# Set the path to your credentials JSON file:
credentials = "twitter_creds.json"
with open(credentials, "r") as keys:
    api_tokens = json.load(keys)
  

API_KEY = api_tokens["api_key"]
API_SECRET = api_tokens["api_secret"]
BEARER_TOKEN = api_tokens["bearer_token"]
ACCESS_TOKEN = api_tokens["access_token"]
ACCESS_SECRET = api_tokens["access_secret"]


# Function to extract tweets
def get_tweets(query, limit):

    client = tweepy.Client(bearer_token=BEARER_TOKEN)

    # Replace with your own search query

    start_time = '2020-01-01T00:00:00Z'
    #end_time = '2020-08-01T00:00:00Z'

    if limit > 100:
        tweets = tweepy.Paginator(client.search_recent_tweets, query=query + ' -is:retweet', tweet_fields=['created_at'], max_results=100).flatten(limit=limit)
    else:
        tweets = client.search_recent_tweets(query=query + ' -is:retweet', max_results=limit)
        print(tweets)

    
    df = pd.DataFrame(columns=['id', 'text', 'query_string'])

    for tweet in tweets:
        row = pd.DataFrame([{'id': tweet.id, 'text': tweet.text, 'query_string': query}])
        df = pd.concat([df, row])   
    

    # filename = '../data/tweets.csv'

    # if os.path.exists(filename):
    #     df.to_csv(filename, mode='a', index=False, header=False)

    # else:    
    #     df.to_csv(filename, mode='w', index=False, header=True)
            


# Driver code
if __name__ == '__main__':
    get_tweets('football', 10)


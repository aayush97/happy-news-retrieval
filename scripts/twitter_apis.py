import tweepy
import json
import pandas as pd

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
def get_tweets(query):
          
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)

    # tweets = tweepy.Cursor(api.search_tweets, 
    #                q="#covid19",
    #                lang='en',
    #                result_type="mixed",
    #                count=100).items(500)

    tweets = api.search_tweets(q="#covid19", count=100)
    print(tweets)


    data = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
    data['len']  = np.array([len(tweet.text) for tweet in tweets])
    data['ID']   = np.array([tweet.id for tweet in tweets])
    data['Date'] = np.array([tweet.created_at for tweet in tweets])
        



# Driver code
if __name__ == '__main__':
    get_tweets("football") 
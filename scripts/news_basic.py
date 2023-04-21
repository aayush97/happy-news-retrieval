import pprint
import requests
import os

secret = os.environ.get("NEWS_API_TOKEN")
url = 'https://newsapi.org/v2/everything?'

def get_news(query):

    resp = []
    categories = ["sports", "nature", "puppies", "cats"]
    if query == "Any":
        for item in categories:
            resp = resp + get_news_modified(item, 5)
            return resp
    else:
        return get_news_modified(query, 20)

def get_news_modified(query, size):
    parameters = {
        'q': query,  # query phrase
        'pageSize': size,  # maximum is 100
        'apiKey': secret  # your own API key
    }

    response = requests.get(url, params=parameters)
    response_json = response.json()

    return response_json

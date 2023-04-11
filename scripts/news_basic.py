import pprint
import requests
import os

secret = os.environ.get("NEWS_API_TOKEN")
url = 'https://newsapi.org/v2/everything?'


def get_news(query):
    parameters = {
        'q': query,  # query phrase
        'pageSize': 20,  # maximum is 100
        'apiKey': secret  # your own API key
    }

    response = requests.get(url, params=parameters)
    response_json = response.json()

    return response_json

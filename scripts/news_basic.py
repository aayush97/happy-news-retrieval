import pprint
import requests 

secret = ''
url = 'https://newsapi.org/v2/everything?'

def get_news(query):
  parameters = {
    'q': query, # query phrase
    'pageSize': 20,  # maximum is 100
    'apiKey': secret # your own API key
  }  

  response = requests.get(url, params=parameters)
  response_json = response.json()
  pprint.pprint(response_json)






# happy-news-retrieval
Retrieve happy news from online sources to promote positivity across the web


###Setup
1. create a database in postgres cli
```
CREATE DATABASE happy_news_retrieval_db;
CREATE USER admin WITH PASSWORD 'admin';
GRANT ALL PRIVILEGES ON DATABASE happy_news_retrieval_db TO admin;
```
2. run init_db.py
```
python init_db.py
```

###twitter api documentation

 - [search_tweets] (https://docs.tweepy.org/en/stable/api.html#tweepy.API.search_tweets)
 	get tweets in the last week

 - [user_timeline] (https://docs.tweepy.org/en/stable/api.html#tweepy.API.user_timeline)
    get tweets for a particular screen name 


 ### flask apis
 
 - ```http
 	GET /tweets 
 	```

   **body** : json
   **example:** 
```javascript
  	{
  		'query'    : "football",
  		'user_id'  : "12345678"

  	}
```

 - ```http
 	POST /click
   ```   

  **body**   : json
  **example**: 
```javascript
  	{
  		'query'    : "football",
  		'tweet_id' : "12A12344",
  		'user_id'  : "12345678"

  	}
```

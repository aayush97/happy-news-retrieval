# happy-news-retrieval
Retrieve happy news from online sources to promote positivity across the web


Setup
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

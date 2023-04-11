import os
import psycopg2

# we can store the credentials in env variables later
conn = psycopg2.connect(
        host="localhost",
        database="happy_news_retrieval_db",
        user="admin",
        password="admin")
        # user=os.environ['DB_USERNAME'],
        # password=os.environ['DB_PASSWORD'])


# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
# cur.execute('CREATE TABLE users (id serial PRIMARY KEY,'
#                                  'name varchar (50) NOT NULL);'
#                                 )

cur.execute('CREATE TABLE users (id serial PRIMARY KEY,'
                          'user_vector BYTEA NOT NULL);')

cur.execute('CREATE TABLE tweets (id serial PRIMARY KEY,'
                                  'twitter_tweet_id bigint NOT NULL,'
                                  'query varchar (50) NOT NULL,'
                                  'document text NOT NULL);'
                                )

cur.execute('CREATE TABLE user_interactions (id serial PRIMARY KEY,'     
                                  'number_of_clicks int NOT NULL,'
                                  'query varchar (50) NOT NULL,'
                                  'category varchar (50) NOT NULL,'
                                  'user_id integer REFERENCES users (id),'
                                  'tweet_id integer REFERENCES tweets (id));'
                                )

# Insert data into the table

cur.execute('INSERT INTO tweets (twitter_tweet_id, query, document)'
            'VALUES (%s, %s, %s)',
            ('1631414076810362883',
             'animals',
             'Ripken the Bat Dog is known for going out to retrieve bats on the field, but this time, he did something a little different. He was there to greet hockey players with high fives as they walked out onto the ice. 11/10 good boi. Catch more Goodable stories on @atmosphere_tv! https://t.co/efmdEIobRC')
            )


conn.commit()

cur.close()
conn.close()

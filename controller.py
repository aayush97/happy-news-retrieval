import os
import psycopg2

conn = psycopg2.connect(host='localhost',
                        database="happy_news_retrieval_db",
                        user="admin",
                        password="admin")


def store_user_profile(user, query, tweet_id):

    cur = conn.cursor()

    sql = """INSERT INTO user_interactions(query, user_id, tweet_id)
             VALUES(%s, %s, %s);"""

    cur.execute(sql, (query, user, tweet_id))
    conn.commit()

    cur.close()
    conn.close()


def store_tweets_returned(user, query, results):
    cur = conn.cursor()

    sql = """INSERT INTO tweets(twitter_tweet_id, query, document)
             VALUES(%s, %s, %s);"""

    for item in results:
        cur.execute(sql, (item['id'], query, item['tweet']))

    conn.commit()

    cur.close()
    conn.close()

def create_user(user, user_vector):
    cur = conn.cursor()

    sql = """INSERT INTO users(id, user_vector)
             VALUES(%s %s);"""

    cur.execute(sql, (user, user_vector))
    conn.commit()

    cur.close()
    conn.close()

def update_user(user, user_vector):
    cur = conn.cursor()

    sql = """UPDATE users
             SET user_vector = %s
             WHERE id = %s;"""

    cur.execute(sql, (user_vector, user))
    conn.commit()

    cur.close()
    conn.close()
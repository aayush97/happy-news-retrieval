import os
import psycopg2
from flask import Flask, request, render_template

app= Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database="happy_news_retrieval_db",
                            user="admin",
                            password="admin")
                            # user=os.environ['DB_USERNAME'],
                            # password=os.environ['DB_PASSWORD']
    return conn


@app.route("/", methods=["POST"])
def retrieve_query_results():
    return "Hi"

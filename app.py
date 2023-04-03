from controller import store_user_profile, store_tweets_returned
import json
import sys
from flask import Flask, request, render_template, jsonify
import psycopg2
import re
import os
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App, Say
from flask import Flask, request
from scripts.twitter_apis import get_tweets
from scripts.sentiment import get_goodness_score


app = Flask(__name__)

bolt_app = App(token=os.environ.get("SLACK_BOT_TOKEN"),
               signing_secret=os.environ.get("SLACK_SIGNING_SECRET"))


@bolt_app.command("/happynews")
def help_command(say, ack):
    ack()
    text = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Choose your category"
                }
            },
            {
                "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                        "type": "plain_text",
                                        "text": "Sports"
                                },
                                "value": "Sports",
                                "action_id": "category_sports"
                            },
                            {
                                "type": "button",
                                "text": {
                                        "type": "plain_text",
                                        "text": "Layoffs"
                                },
                                "value": "Layoffs",
                                "action_id": "category_layoffs"
                            },
                            {
                                "type": "button",
                                "text": {
                                        "type": "plain_text",
                                        "text": "Puppies"
                                },
                                "value": "Puppies",
                                "action_id": "category_puppies"
                            }
                        ]
            },
        ]
    }
    say(text=text)


@bolt_app.action(re.compile("(category)"))
def approve_request(ack, body, say):
    # Acknowledge action request
    ack()
    category = body['actions'][0]['value']
    say("You selected " + category)


handler = SlackRequestHandler(bolt_app)


@ app.route("/slack/events", methods=["POST"])
def slack_events():
    """ Declaring the route where slack will post a request """
    return handler.handle(request)


@ app.route("/", methods=["POST"])
def test_endpoint():
    return "Hi"


def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database="happy_news_retrieval_db",
                            user="admin",
                            password="admin")
    # user=os.environ['DB_USERNAME'],
    # password=os.environ['DB_PASSWORD']
    return conn


"""
api to get top 5 tweets for a query
@request GET
json:
    parameters: user_id, query
@returns top 5 tweets      
"""


@app.route("/tweets")
def retrieve_query_results():
    request_data = request.get_json()
    user_id = request_data['user_id']
    query = request_data['query']

    data = get_tweets(query)

    goodness_Score = get_goodness_score(data)
    sorted_goodness = sorted(goodness_Score, key=lambda x: x['score'])[::-1]

    results = sorted_goodness[:5]
    # store tweets returned in db
    store_tweets_returned(query, results)

    jsonList = json.dumps(results)

    return jsonify(jsonList)


"""
api to store user interaction on clicks
@request POST
json:
    parameters: user_id, tweet_id, query
@returns "Success"   
"""


@app.route("/click", methods=["POST"])
def store_user_profile():
    request_data = request.get_json()
    user_id = request_data['user_id']
    tweet_id = request_data['tweet_id']
    query = request_data['query']

    # store user profile in db
    store_user_profile(user_id, query, tweet_id)
    return "Success", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

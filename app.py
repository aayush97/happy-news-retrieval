import json
from flask import Flask, request, jsonify
import re
import os
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App, Say
from flask import Flask, request
from scripts.twitter_apis import get_tweets
from scripts.sentiment import get_goodness_score
from scripts.news_basic import get_news
import numpy as np
from flask_sqlalchemy import SQLAlchemy
import io
from scripts.user_model import get_initial_user_vector

# database setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://admin:admin@localhost:5432/happy_news_retrieval_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)

from models import *
with app.app_context():
    db.create_all() 


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
                                        "text": "Any"
                                },
                                "value": "Any",
                                "action_id": "category_any"
                            },
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
                                        "text": "Cats"
                                },
                                "value": "Cats",
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


@bolt_app.action("click_feedback")
def record_click(ack, body, say):
    ack()
    user = body['user']
    user_id = user['id']
    user_name = user['username']

    button_clicked = body['actions'][0]['value']

    print(button_clicked)
    print(user)


# @app.route('/user', methods=['POST'])
def add_user(slack_user_id, slack_user_name, user_vector):
    # slack_user_id, slack_user_name, user_vector
    # slack_user_id = 1
    # slack_user_name = "test"
    # user_vector = np.random.rand(1, 300)
    user = User(slack_user_id=slack_user_id,
                slack_user_name=slack_user_name, user_vector=user_vector.tobytes())
    db.session.add(user)
    db.session.commit()
    return (user.serialize)


def update_user(slack_user_id, slack_user_name, user_vector):
    user = User.query.filter_by(slack_user_id=slack_user_id).first()
    user.slack_user_name = slack_user_name
    user.user_vector = user_vector.tobytes()
    db.session.commit()
    return (user.serialize)


@ app.route('/category', methods=['POST'])
def events():
    request_data = request.get_json()
    # user = body['user']
    # category = body['actions'][0]['value']
    category = request_data['action']
    tweet_data = get_tweets(category)

    # Twitter
    tweet_texts = []
    for i in tweet_data:
        tweet_texts.append(i["description"])

    goodness_score = get_goodness_score(tweet_texts)
    for idx, data_row in enumerate(tweet_data):
        data_row["score"] = (goodness_score[idx])

    tweet_data = sorted(tweet_data, key=lambda x: x['score'], reverse=True)

    tweet_data = tweet_data[:5]

    # News
    news_data = get_news(category)
    news_data = news_data['articles']

    news_texts = []
    for i in news_data:
        news_texts.append(i["description"])

    goodness_score = get_goodness_score(news_texts)

    for idx, data_row in enumerate(news_data):
        data_row["score"] = goodness_score[idx]

    news_data = sorted(news_data, key=lambda x: x['score'], reverse=True)
    news_data = news_data[:5]

    total_data = tweet_data + news_data
    total_data = np.random.choice(total_data, size=5, replace=False)
    return jsonify(total_data.tolist())


@bolt_app.action(re.compile("(category)"))
def approve_request(ack, body, say):
    with app.app_context():
        # Acknowledge action request
        ack()
        user = body['user']
        category = body['actions'][0]['value']

        slack_user_id = user['id']
        slack_username = user['username']

        initial_uv = get_initial_user_vector()
        user = User.query.filter_by(slack_user_id=slack_user_id).first()
        print(user.serialize)
        user = add_user(slack_user_id, slack_username, initial_uv)

        print(user)

        tweet_data = get_tweets(category)

        # Twitter
        tweet_texts = []
        for i in tweet_data:
            tweet_texts.append(i["description"])

        goodness_score = get_goodness_score(tweet_texts)

        for idx, data_row in enumerate(tweet_data):
            data_row["score"] = (goodness_score[idx])

        tweet_data = sorted(tweet_data, key=lambda x: x['score'], reverse=True)

        tweet_data = tweet_data[:5]

        # News
        news_data = get_news(category)
        news_data = news_data['articles']

        news_texts = []
        for i in news_data:
            news_texts.append(i["description"])

        goodness_score = get_goodness_score(news_texts)

        for idx, data_row in enumerate(news_data):
            data_row["score"] = goodness_score[idx]

        news_data = sorted(news_data, key=lambda x: x['score'], reverse=True)
        news_data = news_data[:5]

        total_data = tweet_data + news_data
        total_data = np.random.choice(total_data, size=5, replace=False)

        blocks = []
        blocks.append({
            "type": "section",
            "text": {
                    "type": "mrkdwn",
                "text": "*"+category+"*"
            }
        })

        for idx, data in enumerate(total_data):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": data["description"]
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Link to article"
                    },
                    "value": "click_" + str(idx) + "_category",
                    "url": data["url"],
                    "action_id": "click_feedback"
                }
            })
            blocks.append({
                "type": "divider"
            })

        text = {
            "blocks": blocks
        }
        say(text=text)


handler = SlackRequestHandler(bolt_app)


@ app.route("/slack/events", methods=["POST"])
def slack_events():
    """ Declaring the route where slack will post a request """
    return handler.handle(request)


@ app.route("/", methods=["POST"])
def test_endpoint():
    return "Hi"


"""
api to get top 5 tweets for a query
@request GET
json:
    parameters: user_id, query
@returns top 5 tweets
"""

@ app.route("/tweets")
def retrieve_query_results():
    request_data = request.get_json()
    user_id = request_data['user_id']
    query = request_data['query']

    data = get_tweets(query)

    goodness_Score = get_goodness_score(data)
    sorted_goodness = sorted(goodness_Score, key=lambda x: x['score'])[::-1]

    results = sorted_goodness[:5]
    # store tweets returned in db
    tweets = Tweet(query, document=results)
    db.session.add(tweets)
    db.session.commit()

    jsonList = json.dumps(results)

    return jsonify(jsonList)


"""
api to store user interaction on clicks
@request POST
json:
    parameters: user_id, tweet_id, query
@returns "Success"
"""


@ app.route("/click", methods=["POST"])
def store_user_profile():
    request_data = request.get_json()
    user_id = request_data['user_id']
    tweet_id = request_data['tweet_id']
    query = request_data['query']

    # store user profile in db
    interaction = UserInteraction(user_id, query, tweet_id)
    db.session.add(interaction)
    db.session.commit()
    return "Success", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

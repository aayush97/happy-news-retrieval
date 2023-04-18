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
import app
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://admin:admin@localhost:5432/happy_news_retrieval_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    slack_user_id = db.Column(db.String(50), nullable=False)
    slack_user_name = db.Column(db.String(100), nullable=False)
    user_vector = db.Column(db.LargeBinary, nullable=False)

    def __init__(self, slack_user_id, slack_user_name, user_vector):
        self.slack_user_id = slack_user_id
        self.slack_user_name = slack_user_name
        self.user_vector = user_vector

    @property
    def serialize(self):
      return {
          'id': self.id,
          'slack_user_id': self.slack_user_id,
          'slack_user_name': self.slack_user_name,
      }
    
    
class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    article_external_id = db.Column(db.String(50), nullable=False)
    query = db.Column(db.String(100), nullable=False)
    document = db.Column(db.String(1000), nullable=False)


    def __init__(self, article_external_id, query, document):
        self.article_external_id = article_external_id
        self.query = query
        self.document = document
    
    @property
    def serialize(self):
      return {
          'id': self.id,
          'article_external_id': self.article_external_id,
          'query': self.query,
          'document': self.document
      }
    
class Tweet(db.Model):
    __tablename__ = 'tweets'

    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(100), nullable=False)
    documents = db.Column(db.String(1000))
    

    def __init__(self, query, documents):
        self.query = query
        self.documents = documents
    
    @property
    def serialize(self):
      return {
          'id': self.id,
          'query': self.query,
          'documents': self.documents
      }

class UserInteraction(db.Model):
    __tablename__ = 'user_interactions'

    id = db.Column(db.Integer, primary_key=True)
    user_clicked = db.Column(db.Boolean, nullable=False)
    query = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    slack_user_id = db.Column(db.String(50), nullable=False)
    slack_user_name = db.Column(db.String(100), nullable=False)
    article_external_id = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))


    def __init__(self, user_clicked, query, category, slack_user_id, slack_user_name, article_external_id, user_id, article_id):
        self.user_clicked = user_clicked
        self.query = query
        self.category = category
        self.slack_user_id = slack_user_id
        self.slack_user_name = slack_user_name
        self.article_external_id = article_external_id
        self.user_id = user_id
        self.article_id = article_id
       

    @property
    def serialize(self):
      return {
          'id': self.id,
          'user_clicked': self.user_clicked,
          'query': self.query,
          'category': self.category,
          'slack_user_id': self.article_user_id,
          'slack_user_name': self.slack_user_name,
          'article_external_id': self.article_external_id,
          'user_id': self.user_id,
          'article_id': self.article_id
      }

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


@bolt_app.action(re.compile("(category)"))
def approve_request(ack, body, say):
    # Acknowledge action request
    ack()
    user = body['user']
    category = body['actions'][0]['value']

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

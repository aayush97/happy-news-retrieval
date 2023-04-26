from models import *
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
from scripts.user_model import get_initial_user_vector
from scripts.doc2vector import text2vec
from scripts.user_model import update_user_vector_cosine_similarity, get_similarity_between_user_doc_vectors, update_user_vector_category

categories = ["sports", "nature", "puppies", "cats"]
    
    
# database setup
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://admin:admin@localhost:5432/happy_news_retrieval_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# with app.app_context():
#     db.create_all()
# USE THIS ONLY ONCE^

bolt_app = App(token=os.environ.get("SLACK_BOT_TOKEN"),
               signing_secret=os.environ.get("SLACK_SIGNING_SECRET"))

category_blocks = [
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
                                    "text": "Recommended for you"
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
                        },
                        {
                            "type": "button",
                            "text": {
                                    "type": "plain_text",
                                    "text": "Nature"
                            },
                            "value": "Nature",
                            "action_id": "category_nature"
                        },
                    ]
        },
]

def provide_recommendations(client, channel_id, slack_user_id, slack_username, category):
    with app.app_context():
        try:
            client.chat_postEphemeral(
                channel=channel_id,
                user=slack_user_id,
                text= " Processing :dog: "
            )

            user_vector_file = os.path.join(os.getcwd(), f'user_vectors/{slack_user_id}.npy')

            if os.path.isfile(user_vector_file):
                user_vector = np.load(user_vector_file)
            else:
                print(f'{slack_username} didnt exist. Creating user...')
                initial_uv = get_initial_user_vector()
                user_vector = add_user(slack_user_id, initial_uv)

            tweet_data = get_tweets(category)

            # Twitter
            tweet_texts = []
            for i in tweet_data:
                tweet_texts.append(i["description"])

            goodness_score = get_goodness_score(tweet_texts)

            for idx, data_row in enumerate(tweet_data):
                data_row["score"] = (goodness_score[idx])

            tweet_data = sorted(tweet_data, key=lambda x: x['score'], reverse=True)

            tweet_data = tweet_data[:10]

            # News
            news_texts = []

            if category == "Any":
                for item in categories:
                    news_data = get_news(item, 5)
                    news_data = news_data['articles']
                    
                    for i in news_data:
                        news_texts.append(i["description"])
            else:
                news_data = get_news(category, 20)
                news_data = news_data['articles']

                for i in news_data:
                    news_texts.append(i["description"])

            goodness_score = get_goodness_score(news_texts)

            for idx, data_row in enumerate(news_data):
                data_row["score"] = goodness_score[idx]

            news_data = sorted(news_data, key=lambda x: x['score'], reverse=True)
            news_data = news_data[:10]

            total_data = tweet_data + news_data
            #total_data = np.random.choice(total_data, size=5, replace=False)

            #Calculate user doc sim score
            for article in total_data:
                score = get_similarity_between_user_doc_vectors(user_vector, article["description"])
                article["user_doc_sim_score"] = score

            total_data = sorted(total_data, key=lambda x: x['user_doc_sim_score'], reverse=True)
            total_data = total_data[:5]

            for article in total_data:
                article_db = add_article(article["description"])
                article["db_id"] = article_db["id"]

            heading = category

            if heading == "Any":
                heading = "Recommended for you"

            blocks = []
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": heading
                        },
                        "style": "danger",
                        "action_id": "do_nothing"
                    }
                ]
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
                        "value": str(data["db_id"]),
                        "url": data["url"],
                        "action_id": "click_feedback"
                    }
                })
                blocks.append({
                    "type": "divider"
                })

            for i in category_blocks:
                blocks.append(i)

            client.chat_postEphemeral(
                channel=channel_id,
                user=slack_user_id,
                blocks=blocks
            )

            if not category == 'Any':
                print(f"Updating {slack_username} vector with {category}")
                updated_user_vector = update_user_vector_category(user_vector, category)
                add_user(slack_user_id, updated_user_vector)

        except Exception as e:
            text = "Something went wrong. Please try again"
            client.chat_postEphemeral(
                channel=channel_id,
                user=slack_user_id,
                text=text
            )
            print("ERROR")
            print(e)

@bolt_app.command("/happynews")
def help_command(client, ack, body):
    ack()
    channel_id = body['channel_id']
    slack_user_id = body['user_id']
    slack_username = body['user_name']

    user_vector_file = os.path.join(os.getcwd(), f'user_vectors/{slack_user_id}.npy')

    if not os.path.isfile(user_vector_file):
        client.chat_postEphemeral(
            channel=channel_id,
            user=slack_user_id,
            blocks=category_blocks
        )
    else:
        provide_recommendations(client, channel_id, slack_user_id, slack_username, 'Any')


def add_user(slack_user_id, user_vector):
    np.save(os.path.join(os.getcwd(), f'user_vectors/{slack_user_id}'), user_vector)
    return user_vector

def add_article(document, article_external_id ="", query = ""):
    article = Article(document=document,
                      article_external_id=article_external_id, query=query)
    db.session.add(article)
    db.session.commit()
    return (article.serialize)

def add_user_click(slack_user_id, slack_username, document_id):
    interaction = UserInteraction(slack_user_id=slack_user_id,
                      slack_user_name=slack_username, article_id=document_id)
    db.session.add(interaction)
    db.session.commit()
    return (interaction.serialize)

def update_user(slack_user_id, user_vector):
    user = User.query.filter_by(slack_user_id=slack_user_id).first()
    user.user_vector = user_vector.tobytes()
    db.session.commit()
    return (user.serialize)

@bolt_app.action("click_feedback")
def record_click(ack, body, say):
    with app.app_context():
        ack()
        user = body['user']
        slack_user_id = user['id']
        slack_username = user['username']

        user_vector_file = os.path.join(os.getcwd(), f'user_vectors/{slack_user_id}.npy')
        user_vector = np.load(user_vector_file)

        article_no_clicked = body['actions'][0]['value']
        
        article = db.session.query(Article).filter(Article.id==article_no_clicked).first()
        article = article.serialize

        print(f'Updating user vector {slack_username}')

        updated_user_vector = update_user_vector_cosine_similarity(user_vector, article['document'])
        add_user(slack_user_id, updated_user_vector)
        print(add_user_click(slack_user_id, slack_username, article_no_clicked))


@bolt_app.action("do_nothing")
def title(ack):
    ack()


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
    news_texts = []

    if category == "Any":
        for item in categories:
            news_data = get_news(item, 5)
            news_data = news_data['articles']

            for i in news_data:
                news_texts.append(i["description"])
    else:
        news_data = get_news(category, 20)
        news_data = news_data['articles']

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
def approve_request(client, ack, body, say):
    # Acknowledge action request
    ack()
    channel = body['channel']
    channel_id = channel['id']
    user = body['user']
    category = body['actions'][0]['value']
    slack_user_id = user['id']
    slack_username = user['username']

    print(f'{slack_username} clicked on {category}')
    provide_recommendations(client, channel_id, slack_user_id, slack_username, category)


handler = SlackRequestHandler(bolt_app)


@ app.route("/slack/events", methods=["POST"])
def slack_events():
    """ Declaring the route where slack will post a request """
    return handler.handle(request)


@ app.route("/", methods=["GET", "POST"])
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
    app.run(host='0.0.0.0', port=os.environ.get("PORT") or 5000, debug=True)

#http://165.227.139.80

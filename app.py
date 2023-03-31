from flask import Flask, request
from slack_bolt import App, Say
from slack_bolt.adapter.flask import SlackRequestHandler
import os
import re

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
def retrieve_query_results():
    return "Hi"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

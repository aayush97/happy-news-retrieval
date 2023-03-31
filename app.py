from flask import Flask, request
from slack_bolt import App, Say
from slack_bolt.adapter.flask import SlackRequestHandler
import os

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
                    "text": "This is a slash command"
                }
            }
        ]
    }
    say(text=text)


@app.route("/slack/events", methods=["POST"])
def slack_events():
    """ Declaring the route where slack will post a request """
    print("YO")
    return handler.handle(request)


@app.route("/", methods=["POST"])
def retrieve_query_results():
    return "Hi"


handler = SlackRequestHandler(bolt_app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

from flask import Flask, request
from slack_bolt import App, Say
from slack_bolt.adapter.flask import SlackRequestHandler
import os 

app= Flask(__name__)

bolt_app = App(token=os.environ.get("SLACK_BOT_TOKEN"), signing_secret=os.environ.get("SLACK_SIGNING_SECRET"))
handler = SlackRequestHandler(bolt_app)

@app.route("/slacky/events", methods=["POST"])
def slack_events():
    """ Declaring the route where slack will post a request """
    return handler.handle(request)

@app.route("/", methods=["POST"])
def retrieve_query_results():
    return "Hi"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
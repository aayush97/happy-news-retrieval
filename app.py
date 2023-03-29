from flask import Flask, request

app= Flask(__name__)

@app.route("/", methods=["POST"])
def retrieve_query_results():
    return "Hi"
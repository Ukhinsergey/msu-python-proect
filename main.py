from flask import Flask, request
import json
import os
import sys

app = Flask(__name__)

@app.route("/")
def hello():
    return "Pay no attention to that man behind the curtain!"

@app.route("/kek", methods=["GET", "POST"])
def test_handler():
    if request.method == "GET":
        return "my get"
    elif request.method == "POST":
        print('========')
        print(dir(request))
        print(request)
        print(type(request))
        print(request.data)
        print(request.form)
        print('========')
        return 'my post'




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(port)
    print(port, file=sys.stderr)
    app.run(
        host="0.0.0.0", port=port
    )
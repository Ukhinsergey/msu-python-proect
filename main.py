from flask import Flask, request, jsonify
from telegram import Update
from bot import TwitchBot
import os
import json

app = Flask(__name__)
bot = TwitchBot()

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"


@app.route('/telegram', methods=["GET", "POST"])
def telegram_webhook_handler():
    if request.method == "POST":
        update = Update.de_json(request.get_json(), bot.bot)
        bot.updateQueue.put(update)
        return "done"
    elif request.method == "GET":
        return "telegram get"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support

    # port = int(os.environ.get("PORT", 443))
    app.run(
        threaded=True, 
        port=5000
    )

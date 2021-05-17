"""
TODO: Module docstring
"""
import os

from flask import Flask, request
from bot import TwitchBot

app = Flask(__name__)
bot = TwitchBot()

@app.route('/')
def index():
    """A welcome message to test our server"""
    return "<h1>Welcome to our server !!</h1>"

@app.route("/test-webhook", methods=['GET', 'POST'])
def test_author_response():
    """Test webhook example"""
    if request.method == "POST":
        bot.bot.send_message(chat_id=234383022, text='I am working')
    return "ok"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 443))
    app.run(
        threaded=True,
        port=port
    )

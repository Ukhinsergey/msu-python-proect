"""
TODO: Module docstring
"""
import os

from flask import Flask, request
from bot import TwitchBot
from twitch import TwitchApi
import json
app = Flask(__name__)
bot = TwitchBot()
twitch_api = TwitchApi()


@app.route('/')
def index():
    """A welcome message to test our server"""
    return "<h1>Welcome to our server !!</h1>"

@app.route("/test-webhook", methods=['GET', 'POST'])
def test_author_response():
    """Test webhook example"""
    if request.method == "POST":
        bot.bot.send_message(chat_id=234383022, text='I am working')
        bot.bot.send_message(chat_id=456145017, text='I am working')
    return "ok"


@app.route('/twitch_post', methods=['GET', 'POST'])
def twitch_post():
    if request.method == 'POST':
        data = json.loads(request.data)

        twitch_api.info.append(data)
        if "challenge" in data.keys():
            bot.bot.send_message(chat_id=456145017, text=data["challenge"])
            return data["challenge"], 200
        else:
            bot.bot.send_message(chat_id=234383022, text=str(data))
            bot.bot.send_message(chat_id=456145017, text=str(data))
            return "ok",200
    else:
        return 'get ' + str(twitch_api.info), 200


@app.route('/twitch_stat')
def twitch_stat():
    return str(twitch_api.twitch_app_token_json) + str(twitch_api.answ)

@app.route('/post_follow_dean1t')
def post_follow_dean1t():
    twitch_api.get_twitch_user_by_name("dean1t")
    # twitch_api.sub_by_channel_name(42674575)
    return "ok"



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 443))
    app.run(
        threaded=True,
        port=port
    )

"""
TODO: Module docstring
"""
import os

from flask import Flask, request
from bot import TwitchBot
from twitch import TwitchApi
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
            return request.form["challenge"]
        else:
            return "ok"
    else:
        return 'get ' + str(twitch_api.info)


@app.route('/twitch-stat')
def twitch_stat():
    return twitch_api.twitch_app_token_json + str(twitch.answ)

@app.route('/post_follow_dean1t')
def post_follow_dean1t():
    twitch_api.sub_by_channel_name(42674575)



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 443))
    app.run(
        threaded=True,
        port=port
    )

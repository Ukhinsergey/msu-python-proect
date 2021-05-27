"""TODO: Module docstring."""
import os
import json

from flask import Flask, request

from bot import TwitchBot
from twitch import TwitchApi

app = Flask(__name__)
bot = TwitchBot()
twitch_api = TwitchApi(bot)

bot.register_twitch_api(twitch_api)


@app.route('/')
def index():
    """Return a welcome message to test our server."""
    return "<h1>Welcome to our server !!</h1>"

def send_notification(twitch_id: int, display_name: str) -> None:
    """Send a notification to all subscribed users. Updates display_name."""
    subscribed_users = bot.database.get_users_for_sub(twitch_id)

    # Check if display name has changed
    saved_display_name = bot.database.get_channel_name(twitch_id)
    if saved_display_name != display_name:
        bot.database.delete_channel_name(twitch_id)
        bot.database.put_channel_name(twitch_id, display_name)

    for user_id in subscribed_users:
        bot.bot.send_message(
            chat_id=user_id,
            text=f"{display_name} is followed!"
        )

@app.route('/twitch_post', methods=['GET', 'POST'])
def twitch_post():
    """Process main twitch requests."""
    if request.method == 'POST':
        data = json.loads(request.data)

        twitch_api.info.append(data)
        if "challenge" in data.keys():
            return data["challenge"], 200
        else:
            bot.bot.send_message(chat_id=456145017, text=str(data))
            text_messsage = ""
            if data['subscription']['type'] == "channel.follow":
                text_messsage = str(data['event']['user_name']) + " is following " + str(data['event']['broadcaster_user_name'])
                send_notification(int(data['event']['broadcaster_user_id']), data['event']['broadcaster_user_name'])
            elif data['subscription']['type'] == "stream.online":
                text_messsage = str(data['event']['broadcaster_user_name']) + " is streaming now"
            bot.bot.send_message(chat_id=234383022, text=text_messsage)
            bot.bot.send_message(chat_id=456145017, text=text_messsage)
            return "ok", 200
    else:
        return 'get ' + str(twitch_api.info), 200


@app.route('/twitch_stat')
def twitch_stat():
    """Test, will be deleted."""
    return str(twitch_api.twitch_app_token_json) + str(twitch_api.answ)

@app.route('/post_follow_dean1t')
def post_follow_dean1t():
    """Test, will be deleted."""
    # twitch_api.get_twitch_user_by_name("Honeymad")
    twitch_id, display_name = twitch_api.sub_by_channel_name("dean1t")
    bot.bot.send_message(chat_id=456145017, text=str(twitch_id) + ' ' + str(display_name))
    return "ok"

@app.route('/follow_dean1t')
def show_info():
    """Test, will be deleted."""
    return str(twitch_api.check_online("SilverName"))


@app.route('/check_id_silver')
def check_id():
    return str(twitch_api.check_online("SilverName"))


@app.route('/check_id_dean1t')
def check_id():
    return str(twitch_api.check_online("dean1t"))

@app.route('/unsubscribe_all')
def unsubscribe_all():
    """Test, will be deleted."""
    twitch_api.unsubscribe_all()
    return "done"


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 443))
    app.run(
        threaded=True,
        port=port
    )

"""TODO: Module docstring."""
import os
import json

from flask import Flask, request

from bot import TwitchBot
from twitch import TwitchApi

app = Flask(__name__)
bot = TwitchBot()
twitch_api = TwitchApi()

bot.register_twitch_api(twitch_api)
twitch_api.register_bot(bot)


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

        if "challenge" in data.keys():
            return data["challenge"], 200
        else:
            if data['subscription']['type'] == "channel.follow":
                send_notification(int(data['event']['broadcaster_user_id']), data['event']['broadcaster_user_name'])
            elif data['subscription']['type'] == "stream.online":
                pass
            return "ok", 200
    else:
        return 'get', 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 443))
    app.run(
        threaded=True,
        port=port
    )

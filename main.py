"""Main file with Flask application and routes."""
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
    response = twitch_api.check_online(display_name)
    data = response['data'][0]

    # Check if display_name has changed
    saved_display_name = bot.database.get_channel_name(twitch_id)
    if saved_display_name != display_name:
        bot.database.delete_channel_name(twitch_id)
        bot.database.put_channel_name(twitch_id, display_name)

    message = (
        "{display_name} начал трансляцию {game_name}!\n"
        "{title}\n"
        "\n"
        "https://twitch.tv/{display_name}\n"
        .format(
            display_name=display_name,
            game_name=data['game_name'],
            title=data['title']
        )
    )

    for user_id in subscribed_users:
        bot.bot.send_message(
            chat_id=user_id,
            text=message
        )


@app.route('/twitch_post', methods=['POST'])
def twitch_post():
    """Process main twitch requests."""
    data = json.loads(request.data)

    if 'challenge' in data.keys():
        return data['challenge'], 200

    if data['subscription']['type'] == 'stream.online':  # 'channel.follow'
        twitch_id = int(data['event']['broadcaster_user_id'])
        display_name = data['event']['broadcaster_user_name']
        send_notification(twitch_id, display_name)
    return 'ok', 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 443))
    app.run(
        threaded=True,
        port=port
    )

"""TODO: module-docstring."""
import json
import os
import requests


class TwitchApi:
    """Main Twitch API class."""

    def __init__(self):
        """Initialize TwitchAPI instance, update token."""
        self.client_id = os.environ.get("CLIENT_ID", None)
        self.client_secret = os.environ.get("CLIENT_SECRET", None)
        self.bot = None

        token_params = {
            'client_id': self.client_id ,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
        }

        app_token_request = requests.post('https://id.twitch.tv/oauth2/token', params=token_params)
        twitch_app_token_json = app_token_request.json()

        self.headers = {
            'Client-ID': self.client_id,
            'Content-type': 'application/json',
            'Authorization': 'Bearer ' + twitch_app_token_json['access_token']
        }

        self.body = {
            "type": "channel.follow",
            "version": "1",
            "condition": {
                "broadcaster_user_id": "-1"
            },
            "transport": {
                "method": "webhook",
                "callback": "https://pytwitchbot.herokuapp.com/twitch_post",
                "secret": self.client_secret
            }
        }

    def register_bot(self, bot):
        """Register bot instance."""
        self.bot = bot

    def sub_by_channel_name(self, channel):
        """Subscribe to channel (stream.online) by channel name."""
        twitch_id, display_name = self.get_twitch_user_by_name(channel)
        self.sub2(twitch_id)
        return twitch_id, display_name

    def get_twitch_user_by_name(self, channel_name):
        """Get broadcaster_id and display_name by channel name."""
        req = '/helix/users?login='+channel_name
        ans  = requests.get("http://api.twitch.tv" + req, headers = self.headers)
        ans = ans.json()
        if len(ans['data']) == 0:
            raise RuntimeError("no such user")
        return int(ans['data'][0]['id']), ans['data'][0]['display_name']

    def sub(self, twitch_id):
        """Subscribe to channel (channel.follow) by broadcaster_id."""
        self.body['type'] = "channel.follow"
        self.body["condition"]["broadcaster_user_id"] = str(twitch_id)

        json_body = json.dumps(self.body)
        _ = requests.post(
            'https://api.twitch.tv/helix/eventsub/subscriptions',
            data=json_body, headers=self.headers
        )

    def sub2(self, twitch_id):
        """Subscribe to channel (stream.online) by broadcaster_id."""
        self.body['type'] = "stream.online"
        self.body["condition"]["broadcaster_user_id"] = str(twitch_id)

        json_body = json.dumps(self.body)
        _ = requests.post(
            'https://api.twitch.tv/helix/eventsub/subscriptions',
            data=json_body, headers=self.headers
        )

    def unsubscribe_event(self, broadcaster_user_id):
        ans = requests.get(
            "https://api.twitch.tv/helix/eventsub/subscriptions",
            headers = self.headers
        )
        ans = ans.json()
        for i in ans['data']:
            if str(i['condition']['broadcaster_user_id']) == str(broadcaster_user_id):
                adr = i['id']
                answ2 = requests.delete(
                    "https://api.twitch.tv/helix/eventsub/subscriptions?id=" + adr,
                    headers = self.headers
                )
                self.bot.bot.send_message(chat_id=456145017, text=str(answ2))
                self.bot.bot.send_message(chat_id=234383022, text=str(answ2))
            self.bot.bot.send_message(chat_id=456145017, text=str(ans))



    def unsubscribe_all(self):
        """Unsubscribe from all events (admins-only)."""
        ans = requests.get(
            "https://api.twitch.tv/helix/eventsub/subscriptions",
            headers = self.headers
        )
        ans = ans.json()
        for i in ans['data']:
            adr = i['id']
            answ2 = requests.delete(
                "https://api.twitch.tv/helix/eventsub/subscriptions?id=" + adr,
                headers = self.headers
            )
            self.bot.bot.send_message(chat_id=456145017, text=str(answ2))
            self.bot.bot.send_message(chat_id=234383022, text=str(answ2))

    def check_online(self, channel_name):
        """Check if channel 'channel_name' is online."""
        twitch_id, _ = self.get_twitch_user_by_name(channel_name)
        req = 'https://api.twitch.tv/helix/streams?user_id='+str(twitch_id)
        ans = requests.get(req, headers =self.headers)
        ans = ans.json()
        return ans

import json
import os
import requests


class TwitchApi:

    def __init__(self, bot = None):
        self.client_id = os.environ.get("CLIENT_ID", None)
        self.client_secret = os.environ.get("CLIENT_SECRET", None) 
        self.info = []
        self.answ = []
        self.channel_names = []
        self.bot = bot
        token_params = {
            'client_id': self.client_id ,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
        }
        app_token_request = requests.post('https://id.twitch.tv/oauth2/token', params=token_params)
        self.twitch_app_token_json = app_token_request.json()

        self.headers = {
            'Client-ID': self.client_id,
            'Content-type': 'application/json',
            'Authorization': 'Bearer ' + self.twitch_app_token_json['access_token']
        }

        self.body = {
            "type": "channel.follow",
            "version": "1",
            "condition": {
                "broadcaster_user_id": "42674575"
            },
            "transport": {
                "method": "webhook",
                "callback": "https://pytwitchbot.herokuapp.com/twitch_post",
                "secret": self.client_secret 
            }
        }

    def sub_by_channel_name(self, channel):
        twitch_id, display_name = self.get_twitch_user_by_name(channel)
        self.sub2(twitch_id)
        return int(twitch_id), display_name

    def get_twitch_user_by_name(self, channel_name):
        """get_twitch_user_by_name"""
        req = '/helix/users?login='+channel_name
        ans  = requests.get("http://api.twitch.tv" + req, headers = self.headers)
        ans = ans.json()
        self.channel_names.append(ans)
        if len(ans['data']) == 0: 
            raise RuntimeError("no such user")
        return ans['data'][0]['id'], ans['data'][0]['display_name']

    def sub(self, twitch_id):
        self.body['type'] = "channel.follow"
        self.body["condition"]["broadcaster_user_id"] = str(twitch_id)
        json_body = json.dumps(self.body)
        ans = requests.post('https://api.twitch.tv/helix/eventsub/subscriptions', data=json_body, headers=self.headers)
        ans = ans.json()
        self.answ.append(ans)

    def sub2(self, twitch_id):
        self.body['type'] = "stream.online"
        self.body["condition"]["broadcaster_user_id"] = str(twitch_id)
        json_body = json.dumps(self.body)
        ans = requests.post('https://api.twitch.tv/helix/eventsub/subscriptions', data=json_body, headers=self.headers)
        ans = ans.json()
        self.answ.append(ans)


    def unsubscribe_all(self):
        ans = requests.get("https://api.twitch.tv/helix/eventsub/subscriptions", headers = self.headers)
        ans = ans.json()
        for i in ans['data']:
            adr = i['id']
            answ2 = requests.delete("https://api.twitch.tv/helix/eventsub/subscriptions?id=" + adr, headers = self.headers)
            self.bot.bot.send_message(chat_id=456145017, text=str(answ2))
            self.bot.bot.send_message(chat_id=234383022, text=str(answ2))


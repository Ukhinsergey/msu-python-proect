import json
import os
import requests




class TwitchApi:
    def __init__(self):
        self.client_id = os.environ.get("CLIENT_ID", None)
        self.client_secret = os.environ.get("CLIENT_SECRET", None) 
        self.info = []
        self.answ = []
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
        twitch_id = self.getid_by_channel_name(channel)
        self.sub(twitch_id)


    def sub(self, twitch_id):
        self.body["condition"]["broadcaster_user_id"] = str(twitch_id)
        json_body = json.dumps(self.body)
        ans = requests.post('https://api.twitch.tv/helix/eventsub/subscriptions' ,data=json_body, headers=self.headers)
        ans = ans.json()
        self.answ.append(ans)


    def getid_by_channel_name(self, channel):
        return channel



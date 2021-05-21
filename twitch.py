import requests
import json
import os




class TwitchApi:
    def __init__(self):
        self.client_id = os.environ.get("CLIENT_ID", None)
        self.client_secret = os.environ.get("CLIENT_SECRET", None) 
        token_params = {
            'client_id': self.client_id ,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
        }
        app_token_request = requests.post('https://id.twitch.tv/oauth2/token', params=token_params)
        self.twitch_app_token_json = app_token_request.json()

        self.headers = {
            'Client-ID': self.clientid,
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
                "callback": "https://heroku-testing-app228.herokuapp.com/",
                "secret": self.client_secret 
            }
        }

import urllib.parse
import requests

from functools import lru_cache
from collections import namedtuple
from typing import Dict, Tuple

from i_cant_chat.settings import CLIENT_ID, CLIENT_SECRET


DiscordUserType = namedtuple('DiscordUserType', ['id', 'username', 'avatar'])
DiscordTokenType = namedtuple('DiscordTokenType', [
    'access_token', 'token_type', 'expires_in', 'refresh_token', 'scope'
])


class DiscordApiError(Exception):
    def __init__(self, message, code=-1):
        self.message = message
        self.code = code

    def __str__(self):
        return f"({self.code}) {self.message}"


class DiscordApi:
    API_URL = 'https://discord.com/api/v6'
    USER_OAUTH2_URL = "/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=identify%20email"
    TOKEN_URL = "/oauth2/token"

    def __init__(self, client_id: str, client_secret: str):
        self._client_id = client_id
        self._client_secret = client_secret
    
    @staticmethod
    @lru_cache(maxsize=32)
    def get_auth_headers(user_auth_token: str) -> Dict[str, str]:
        return {
            "User-Agent": "ICantChatDiscordApi (i-cant-chat.herokuapp.com, 1)",
            "Authorization": f"Bearer {user_auth_token}"
        }

    @staticmethod
    def raise_response_error(response):
        if "message" in response:
            raise DiscordApiError(**response)
        else:
            raise DiscordApiError(response)

    @staticmethod
    def request_token(data) -> DiscordTokenType:
        response = requests.post(
            DiscordApi.API_URL + DiscordApi.TOKEN_URL,
            data=data, headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )

        try:
            json_response = response.json()
            if response.ok:
                return DiscordTokenType(**json_response)
            DiscordApi.raise_response_error(json_response)
        except ValueError:
            raise DiscordApiError(response.text)

    def get_auth_url(self, redirect_uri: str) -> str:
        return self.API_URL + self.USER_OAUTH2_URL.format(
            client_id=self._client_id,
            redirect_uri=urllib.parse.quote(redirect_uri)
        )

    def get_access_token(self, code: str, redirect_uri: str) -> DiscordTokenType:
        return DiscordApi.request_token({
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'scope': 'identify email'
        })

    def refresh_token(self, refresh_token: str, redirect_uri: str) -> DiscordTokenType:
        return DiscordApi.request_token({
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'redirect_uri': redirect_uri,
            'scope': 'identify email'
        })

    def _process_user_response(self, response) -> DiscordUserType:
        try:
            json_response = response.json()
            if response.ok:
                return DiscordUserType(
                    id=json_response['id'],
                    username=json_response['username'],
                    avatar=json_response['avatar']
                )
            DiscordApi.raise_response_error(json_response)
        except ValueError:
            raise DiscordApiError(response.text)

    def get_user(self, user_auth_token: str) -> DiscordUserType:
        current_user_api_url = self.API_URL + "/users/@me"
        auth_headers = DiscordApi.get_auth_headers(user_auth_token)
        response = requests.get(current_user_api_url, headers=auth_headers)
        return self._process_user_response(response)

    def change_username(self, user_auth_token: str, username: str) -> DiscordUserType:
        change_username_api_url = self.API_URL + "/users/@me"
        auth_headers = DiscordApi.get_auth_headers(user_auth_token)
        print(auth_headers)
        response = requests.patch(change_username_api_url, 
            headers=auth_headers, data=f"{{'username': {username}}}"
        )
        print(response.text)
        return self._process_user_response(response)


API = DiscordApi(CLIENT_ID, CLIENT_SECRET)

import requests
import json
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, order=True)
class JWT:
    access_token: str
    refresh_token: str
    request_time: datetime


class JWTStorage:
    __instance = None
    __is_init = False

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, login_id, login_pwd):
        cls = type(self)
        if not cls.__is_init:
            cls.__is_init = True
            print('JWTStorage created')

            self.__login_id = login_id
            self.__login_pwd = login_pwd
            self.__jwt = JWT('', '', datetime.now())
            self.login_url = 'https://searchad.naver.com/auth/login'
            self.auth_url = 'https://atower.searchad.naver.com/auth/local/extend'
            self.headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/100.0.4896.127 Safari/537.36',
                'content-type': 'application/json'
            }

    def set_init_tokens(self):
        payload = json.dumps({
            'loginId': f'{self.__login_id}',
            'loginPwd': f'{self.__login_pwd}'
        }, separators=(',', ':'))

        with requests.post(url=self.login_url, headers=self.headers, data=payload) as response:
            if (res_code := response.status_code) != 200:
                print(response.text, flush=True)
                self.__jwt = JWT(access_token=str(res_code), refresh_token='', request_time=datetime.now())
                return self

            tokens = json.loads(response.text)
            self.__jwt = JWT(access_token=tokens['token'], refresh_token=tokens['refreshToken'], request_time=datetime.now())
            return self

    def set_new_tokens(self, prev_token):
        param = {'refreshToken': f'{prev_token}'}

        with requests.put(url=self.auth_url, headers=self.headers, params=param) as response:
            if (res_code := response.status_code) != 200:
                print(response.text, flush=True)
                self.__jwt = JWT(access_token=str(res_code), refresh_token='', request_time=datetime.now())
                return self

            tokens = json.loads(response.text)
            self.__jwt = JWT(access_token=tokens['token'], refresh_token=tokens['refreshToken'], request_time=datetime.now())
            return self

    def get_tokens(self):
        return self.__jwt

    def get_access_token(self):
        return self.__jwt.access_token

    def get_refresh_token(self):
        return self.__jwt.refresh_token

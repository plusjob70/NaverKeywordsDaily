import hmac
import hashlib
import base64
import requests
import time
from typing import Union


class RelKwdStat:
    def __init__(self, _customer_id: str, _access_licence: str, _secret_key: str):
        self.url = 'https://api.naver.com/keywordstool'
        self.__customer_id = _customer_id
        self.__access_licence = _access_licence
        self.__secret_key = _secret_key

    def __generate_signature(self, time_stamp: int):
        signature = hmac.new(self.__secret_key.encode(),
                             f"{time_stamp}.GET./keywordstool".encode(),
                             hashlib.sha256).digest()
        return base64.b64encode(signature).decode()

    def __generate_headers(self, time_stamp: int):
        return {
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Timestamp': str(time_stamp),
            'X-API-KEY': self.__access_licence,
            'X-Customer': self.__customer_id,
            'X-Signature': self.__generate_signature(time_stamp)
        }

    # click_count_dict = {'keyword' : [PC_Monthly_Click_Count, MO_Monthly_Click_Count]}
    def request(self, _keyword_list):
        time_stamp = int(round(time.time() * 1000))
        params = {
            'siteId': self.__customer_id,
            'hintKeywords': ','.join(_keyword_list),
            'showDetail': 0
        }

        with requests.get(url=self.url, headers=self.__generate_headers(time_stamp), params=params) as response:
            if (res_code := response.status_code) == 200:
                click_count_dict = {keyword: [0, 0] for keyword in _keyword_list}

                results = response.json().get('keywordList')
                for result in results:
                    rel_keyword: str = result.get('relKeyword')
                    if rel_keyword in _keyword_list:
                        mpc: Union[int, str] = result.get('monthlyPcQcCnt')
                        mmc: Union[int, str] = result.get('monthlyMobileQcCnt')

                        if type(mpc) is int:
                            click_count_dict[rel_keyword][0] = mpc
                        else:
                            print(f'pc_click_count = \'{rel_keyword}\': ({mpc}) -> 0')

                        if type(mmc) is int:
                            click_count_dict[rel_keyword][1] = mmc
                        else:
                            print(f'mo_click_count = \'{rel_keyword}\': ({mmc}) -> 0')
                    else:
                        break
                print(f'{click_count_dict = }')
                return click_count_dict, res_code
            else:
                print(f'{res_code = }')
                return None, res_code

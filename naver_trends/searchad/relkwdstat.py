import hmac
import hashlib
import base64
import requests
import time
from typing import Union


class RelKwdStat:
    def __init__(self, _customer_id: str, _access_licence: str, _secret_key: str, _keyword_list=None):
        self.url = 'https://api.naver.com/keywordstool'
        self.customer_id = _customer_id
        self.access_licence = _access_licence
        self.secret_key = _secret_key
        self.keyword_list = _keyword_list
        self.time_stamp = int(round(time.time() * 1000))
        self.query = self.__generate_query()
        self.header = self.__generate_header()

    def __generate_signature(self):
        signature = hmac.new(self.secret_key.encode(),
                             f"{self.time_stamp}.GET./keywordstool".encode(),
                             hashlib.sha256).digest()
        return base64.b64encode(signature).decode()

    def __generate_header(self):
        return {
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Timestamp': str(self.time_stamp),
            'X-API-KEY': self.access_licence,
            'X-Customer': self.customer_id,
            'X-Signature': self.__generate_signature()
        }

    def __generate_query(self):
        keywords = ','.join(self.keyword_list).replace(' ', '')
        return f'?siteId={self.customer_id}&hintKeywords={keywords}&showDetail=0'

    # click_count_dict = {'keyword' : [PC_Monthly_Click_Count, MO_Monthly_Click_Count]}
    def request(self):
        response = requests.get(f'{self.url}{self.query}', headers=self.header)
        res_code = response.status_code

        if res_code == 200:
            click_count_dict = {keyword: [0, 0] for keyword in self.keyword_list}
            results = response.json().get('keywordList')

            for result in results:
                rel_keyword: str = result.get('relKeyword')
                if rel_keyword in self.keyword_list:
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

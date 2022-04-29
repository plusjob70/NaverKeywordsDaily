import json
import requests
import pandas as pd
from naver_trends.common.constant import UID, UPW
from naver_trends.common.uinfo import CUSTOMER_LIST
from naver_trends.searchad.relkwdstat_detail.jwt import JWTStorage


class RelkwdstatDetail:
    @classmethod
    def customer_info(cls):
        if CUSTOMER_LIST:
            return CUSTOMER_LIST[0][UID], CUSTOMER_LIST[0][UPW]
        return '', ''

    def __init__(self):
        self.token_storage = JWTStorage(*self.__class__.customer_info()).set_init_tokens()
        self.url = 'https://manage.searchad.naver.com/keywordstool'
        self.headers = {
            'authorization': f'Bearer {self.token_storage.get_access_token()}',
        }
        self.params = {
            'format': 'json',
            'includeHintKeywords': 0,
            'showDetail': 1,
        }

    def __change_access_token(self):
        self.token_storage.set_new_tokens(self.token_storage.get_refresh_token())
        self.headers['authorization'] = f'Bearer {self.token_storage.get_access_token()}'
        print('access token is changed')

    # get monthly click count about detail attribute (age, gender, device)
    def get_detail_data(self, keyword: str, scopes: list = None):
        self.params['keyword'] = keyword
        df = pd.DataFrame(columns=['age', 'gender', 'device', 'count'])

        if scopes is None:
            scopes = ['age', 'gender', 'device']

        with requests.get(url=self.url, headers=self.headers, params=self.params) as response:
            if (res_code := response.status_code) == 401:
                self.__change_access_token()
                response = requests.get(url=self.url, headers=self.headers, params=self.params)
            elif res_code != 200:
                print(response.text)
                return df

            data = json.loads(response.text)['keywordList'][0]['userStat']

            if not ((age_group_list := data['ageGroup']) and (gender_type_list := data['genderType'])):
                return df

            monthly_pc_cnt_list = data['monthlyPcQcCnt']
            monthly_mo_cnt_list = data['monthlyMobileQcCnt']

            df['age'] = age_group_list * 2
            df['gender'] = gender_type_list * 2
            df['device'] = ['PC'] * len(monthly_pc_cnt_list) + ['모바일'] * len(monthly_mo_cnt_list)
            df['count'] = monthly_pc_cnt_list + monthly_mo_cnt_list
        return df.groupby(scopes).sum()

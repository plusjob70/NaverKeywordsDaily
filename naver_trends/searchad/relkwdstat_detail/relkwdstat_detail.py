import time
import requests
import pandas as pd
from naver_trends.searchad.relkwdstat_detail.jwt import JWTStorage


class RelkwdstatDetail:
    def __init__(self, customer_id, customer_pwd):
        self.token_storage = JWTStorage(customer_id, customer_pwd).set_init_tokens()
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
    def request(self, _keyword_list, scopes: list = None):
        if scopes is None:
            scopes = ['age', 'device', 'gender']
        else:
            scopes.sort()

        click_count_dict = {keyword: None for keyword in _keyword_list}

        for keyword in _keyword_list:
            self.params['keyword'] = keyword
            df = pd.DataFrame(columns=['age', 'device', 'gender', f'{keyword}'])

            with requests.get(url=self.url, headers=self.headers, params=self.params) as response:
                if (res_code := response.status_code) == 200:
                    pass
                elif res_code == 401:
                    self.__change_access_token()
                    response = requests.get(url=self.url, headers=self.headers, params=self.params)
                elif res_code == 429:
                    print('too fast request. wait 3 seconds...')
                    time.sleep(3)
                    response = requests.get(url=self.url, headers=self.headers, params=self.params)
                else:
                    print(response.text)
                    continue

                data = response.json()['keywordList'][0]['userStat']
                if not ((age_group_list := data['ageGroup']) and (gender_type_list := data['genderType'])):
                    continue

                monthly_pc_cnt_list = data['monthlyPcQcCnt']
                monthly_mo_cnt_list = data['monthlyMobileQcCnt']

                df['age'] = age_group_list * 2
                df['device'] = ['PC'] * len(monthly_pc_cnt_list) + ['모바일'] * len(monthly_mo_cnt_list)
                df['gender'] = gender_type_list * 2
                df[f'{keyword}'] = monthly_pc_cnt_list + monthly_mo_cnt_list

                df = df.groupby(scopes).sum()

                if not df.empty:
                    click_count_dict.update(df.to_dict())

        return click_count_dict

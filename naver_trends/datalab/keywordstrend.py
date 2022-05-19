import requests
from itertools import dropwhile
from datetime import date, timedelta, datetime
from naver_trends.common.constant import *


class Keywordstrend:
    def __init__(self, _client_id: str, _client_secret: str):
        self.url = 'https://openapi.naver.com/v1/datalab/search'
        self.__client_id = _client_id
        self.__client_secret = _client_secret

    """
    device = 'pc' or 'mo'
    gender = 'm' or 'f'
    ages = ['1' ~ '11']
        '1' : 0~12세
        '2' : 13~18세
        '3' : 19~24세
        '4' : 25~29세
        '5' : 30~34세
        '6' : 35~39세
        '7' : 40~44세
        '8' : 45~49세
        '9' : 50~54세
        '10' : 55~59세
        '11' : 60세~
    """
    @staticmethod
    def __generate_body(keyword_list, device: str, gender: str, ages: list[str], start_date: date) -> dict:
        body = {
            'startDate': str(start_date),
            'endDate': str(YESTERDAY.date()),
            'timeUnit': 'date',
            'keywordGroups': [{'groupName': keyword, 'keywords': [keyword]} for keyword in keyword_list],
        }
        if device is not None:
            body['device'] = device
        if gender is not None:
            body['gender'] = gender
        if ages is not None:
            body['ages'] = ages
        return body

    def __generate_headers(self):
        return {
            'Content-Type': 'application/json',
            'X-Naver-Client-Id': self.__client_id,
            'X-Naver-Client-Secret': self.__client_secret
        }

    def request(self, _keyword_list, _device: str = None, _gender: str = None, _ages: list[str] = None, latest_date_dict=None):
        # set oldest latest date
        if latest_date_dict is None:
            latest_date_dict = {}

        if latest_date_dict and (len(latest_date_dict) == len(_keyword_list)):
            oldest_latest_date = datetime.strptime(min(latest_date_dict.values()), '%Y-%m-%d') \
                                 + timedelta(hours=10, minutes=0)
            if (oldest_latest_date + timedelta(days=30)) > YESTERDAY:
                oldest_latest_date = YESTERDAY - timedelta(days=29)
        else:
            oldest_latest_date = DEFAULT_START_DATE

        # request to Naver keywords trend API
        with requests.post(url=self.url,
                           headers=self.__generate_headers(),
                           json=self.__generate_body(keyword_list=_keyword_list, device=_device, gender=_gender,
                                                     ages=_ages, start_date=oldest_latest_date.date())) as response:

            if (res_code := response.status_code) == 200:
                """
                initialize dr_dict(Daily Ratio Dictionary) and mr_dict(Monthly Ratio Dictionary)
                dr_dict = {keyword1 : {str(date1) : float(ratio1)}, {str(date2) : float(ratio2)}, ...}
                mr_dict = {keyword1 : float(MR1), keyword2 : float(MR2), ...}
                zero_dict is all zero value dictionary because Naver API doesn't provide "dates" with zero values.
                """
                dr_dict, mr_dict, zero_dict = {}, {}, None

                # initialize zero_dict for mr_dict
                if (oldest_latest_date + timedelta(days=30)) > YESTERDAY:
                    zero_dict = {str(YESTERDAY.date() - timedelta(day)): 0 for day in range(29, -1, -1)}
                else:
                    day_diff: int = (NOW - oldest_latest_date).days
                    zero_dict = {str(oldest_latest_date.date() + timedelta(days=day)): 0 for day in range(day_diff)}

                # set dr_dict and mr_dict
                results = response.json().get('results')
                for result in results:
                    keyword: str = result.get('title')
                    latest_date: str = latest_date_dict.get(keyword, str(DEFAULT_LATEST_DATE))

                    ratio_dict = zero_dict.copy()
                    real_dict = {data.get('period'): data.get('ratio') for data in result.get('data')}
                    ratio_dict.update(real_dict)

                    mr_dict[keyword] = sum(list(ratio_dict.values())[-30:])
                    dr_dict[keyword] = dict(dropwhile(lambda x: x[0] <= latest_date, ratio_dict.items()))
                print(f'{_device}, {_gender}, {_ages} : {mr_dict = }')
                return dr_dict, mr_dict, res_code

            else:
                print(f'Keywordstrend-request : {res_code = }', flush=True)
                return None, None, res_code

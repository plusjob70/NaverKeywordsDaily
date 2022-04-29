import json
import urllib.request as urlreq
from urllib.error import HTTPError
from datetime import date, timedelta, datetime
from naver_trends.common.constant import *


class Keywordstrend:
    def __init__(self, _client_id: str, _client_secret: str, _keyword_list=None):
        self.url = 'https://openapi.naver.com/v1/datalab/search'
        self.client_id = _client_id
        self.client_secret = _client_secret
        self.keyword_list = _keyword_list

    """
    device = 'pc' or 'mo'
    gender = 'm' or 'f'
    ages = [1 ~ 11]
        1 : 0~12세
        2 : 13~18세
        3 : 19~24세
        4 : 25~29세
        5 : 30~34세
        6 : 35~39세
        7 : 40~44세
        8 : 45~49세
        9 : 50~54세
        10 : 55~59세
        11 : 60세~
    """
    def __generate_body(self, device: str, gender: str, ages: list[int], start_date: date) -> bytes:
        keyword_groups = [f"{{\"groupName\":\"{keyword}\",\"keywords\":[\"{keyword}\"]}}"
                          for keyword in self.keyword_list]
        return f"{{\
            \"startDate\":\"{str(start_date)}\",\
            \"endDate\":\"{str(YESTERDAY.date())}\",\
            \"timeUnit\":\"date\",\
            {Q + 'device' + Q + ':' + Q + device + Q + ',' if (device is not None) else ''}\
            {Q + 'gender' + Q + ':' + Q + gender + Q + ',' if (gender is not None) else ''}\
            {Q + 'ages' + Q + ':' + str([f'{Q+ str(age) +Q}' for age in ages]) + ',' if (ages is not None) else ''}\
            \"keywordGroups\":{keyword_groups}\
        }}".replace("\'", "").encode('utf-8')

    def request(self, _device: str = None, _gender: str = None, _ages: list = None, latest_date_dict: dict = None):
        if latest_date_dict is None:
            latest_date_dict = {}

        request = urlreq.Request(self.url)
        request.add_header('X-Naver-Client-Id', self.client_id)
        request.add_header('X-Naver-Client-Secret', self.client_secret)
        request.add_header('Content-Type', 'application/json')

        try:
            # set oldest latest date
            if latest_date_dict and (len(latest_date_dict) == len(self.keyword_list)):
                oldest_latest_date = datetime.strptime(min(latest_date_dict.values()), '%Y-%m-%d') \
                                     + timedelta(hours=10, minutes=0)
                if (oldest_latest_date + timedelta(days=30)) > YESTERDAY:
                    oldest_latest_date = YESTERDAY - timedelta(days=29)
            else:
                oldest_latest_date = DEFAULT_START_DATE

            # request
            response = urlreq.urlopen(request, data=self.__generate_body(device=_device,
                                                                         gender=_gender,
                                                                         ages=_ages,
                                                                         start_date=oldest_latest_date.date()))
            res_code = response.getcode()

            """
            initialize dr_dict(Daily Ratio Dictionary) and mr_dict(Monthly Ratio Dictionary)
            dr_dict = {keyword1 : {str(date1) : float(ratio1)}, {str(date2) : float(ratio2)}, ...}
            mr_dict = {keyword1 : float(MR1), keyword2 : float(MR2), ...}
            zero_dict is all zero value dictionary because Naver API doesn't provide "dates" with zero values.
            """
            dr_dict, mr_dict, zero_dict = {}, {}, None

            # initialize zero_dict for mr_dict
            if (oldest_latest_date + timedelta(days=30)) > YESTERDAY:
                zero_dict = {str(YESTERDAY.date() - timedelta(day)): 0 for day in range(30)}
            else:
                day_diff: int = (NOW - oldest_latest_date).days
                zero_dict = {str(oldest_latest_date.date() + timedelta(days=day)): 0 for day in range(day_diff)}

            # set dr_dict and mr_dict
            results = json.loads(response.read()).get('results')
            for result in results:
                keyword: str = result.get('title')
                latest_date: str = latest_date_dict.get(keyword, str(DEFAULT_LATEST_DATE))

                ratio_dict = zero_dict.copy()
                real_dict = {data.get('period'): data.get('ratio') for data in result.get('data')}
                ratio_dict.update(real_dict)

                mr_dict[keyword] = sum(list(ratio_dict.values())[-30:])
                dr_dict[keyword] = dict(filter(lambda x: x[0] > latest_date, ratio_dict.items()))
            print(f'{_device}, {_gender}, {_ages} : {mr_dict = }')
            return dr_dict, mr_dict, res_code

        except HTTPError as error:
            print(f'Keywordstrend-request : {error = }', flush=True)
            return None, None, error.code

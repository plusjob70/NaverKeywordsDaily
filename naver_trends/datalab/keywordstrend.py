import json
import urllib.request as UR
from datetime import date, timedelta, datetime
from common.constant import *

class Keywordstrend:
    def __init__(self, client_id : str, client_secret : str, keyword_list=None):
        self.url           = 'https://openapi.naver.com/v1/datalab/search'
        self.client_id     = client_id
        self.client_secret = client_secret
        self.keyword_list  = keyword_list

    def generate_body(self, device : str, start_date : date) -> str:
        keyword_groups = [f"{{\"groupName\":\"{keyword}\",\"keywords\":[\"{keyword}\"]}}" for keyword in self.keyword_list]
        return f"{{\
            \"startDate\":\"{str(start_date)}\",\
            \"endDate\":\"{str(YESTERDAY.date())}\",\
            \"timeUnit\":\"date\",\
            \"keywordGroups\":{keyword_groups},\
            \"device\":\"{device}\"\
        }}".replace("\'", "").encode('utf-8')
    
    def request(self, device : str, latest_date_dict : dict):
        request = UR.Request(self.url)
        request.add_header('X-Naver-Client-Id', self.client_id)
        request.add_header('X-Naver-Client-Secret', self.client_secret)
        request.add_header('Content-Type', 'application/json')
        
        try:
            # set oldest latest date
            if (latest_date_dict is not None):
                if (len(latest_date_dict) != len(self.keyword_list)):
                    oldest_latest_date = DEFAULT_START_DATE
                else:
                    oldest_latest_date = datetime.strptime(min(latest_date_dict.values()), '%Y-%m-%d') + timedelta(hours=10, minutes=0)
                    if (oldest_latest_date + timedelta(days=30) > YESTERDAY):
                        oldest_latest_date = YESTERDAY - timedelta(days=29)
            else:
                oldest_latest_date = DEFAULT_START_DATE

            # request
            response = UR.urlopen(request, data=self.generate_body(device, oldest_latest_date.date()))
            res_code = response.getcode()

            # initialize ratio_dict(Daily Ratio Dictionary) and mr_dict(Monthly Ratio Dictionary)
            ratio_dict = {keyword:dict for keyword in self.keyword_list}
            mr_dict    = {keyword:dict for keyword in self.keyword_list}

            # initialize zero_dict for mr_dict
            if (oldest_latest_date + timedelta(days=30) > YESTERDAY):
                zero_dict = {str(YESTERDAY.date() - timedelta(day)):0 for day in range(30)}
            else:
                day_diff  = (NOW - oldest_latest_date).days
                zero_dict = {str(oldest_latest_date.date() + timedelta(days=day)):0 for day in range(day_diff)}

            # set ratio_dict and mr_dict
            results = json.loads(response.read()).get('results')
            for result in results:
                keyword     = result.get('title')
                latest_date = str(DEFAULT_LATEST_DATE)

                if (latest_date_dict is not None):
                    latest_date = latest_date_dict.get(keyword, latest_date)

                dr_dict   = zero_dict.copy()
                real_dict = {data.get('period'):data.get('ratio') for data in result.get('data')}
                dr_dict.update(real_dict)

                mr_dict[keyword]    = sum(list(dr_dict.values())[-30:])
                ratio_dict[keyword] = dict(filter(lambda x: x[0] > latest_date, dr_dict.items()))
            return ratio_dict, mr_dict, res_code

        except UR.HTTPError as e:
            # print('Http Error:', e.code)
            return None, None, e.code

if __name__ == '__main__':
    from pprint import pprint

    client_id = ''
    client_secret = ''
    keyword_list = ['']

    kt = Keywordstrend(client_id=client_id, client_secret=client_secret, keyword_list=keyword_list)

    request = UR.Request(kt.url)
    request.add_header('X-Naver-Client-Id', kt.client_id)
    request.add_header('X-Naver-Client-Secret', kt.client_secret)
    request.add_header('Content-Type', 'application/json')

    response = UR.urlopen(request, data=kt.generate_body('pc'))
    results = json.loads(response.read()).get('results')

    pprint(results)
import urllib.request as UR
from datetime import date, timedelta
import json
from constant import START_DATE, DAY_DIFF, DEFAULT_LATEST_DATE

class Keywordstrend:
    def __init__(self, client_id : str, client_secret : str, keyword_list=None):
        self.url           = 'https://openapi.naver.com/v1/datalab/search'
        self.client_id     = client_id
        self.client_secret = client_secret
        self.keyword_list  = keyword_list
        self.start_date    = str(START_DATE)
        self.end_date      = str(date.today() - timedelta(1))

    def generate_body(self, device : str) -> str:
        keyword_groups = [f"{{\"groupName\":\"{keyword}\",\"keywords\":[\"{keyword}\"]}}" for keyword in self.keyword_list]
        return f"{{\
            \"startDate\":\"{self.start_date}\",\
            \"endDate\":\"{self.end_date}\",\
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
            response = UR.urlopen(request, data=self.generate_body(device))
            res_code = response.getcode()

            ratio_dict = {keyword:dict for keyword in self.keyword_list}
            mr_dict    = {keyword:dict for keyword in self.keyword_list}
            zero_dict  = {str(START_DATE + timedelta(day)):0 for day in range(DAY_DIFF)}
            results    = json.loads(response.read()).get('results')

            for result in results:
                keyword     = result.get('title')
                latest_date = DEFAULT_LATEST_DATE

                if (latest_date_dict != None):
                    latest_date = latest_date_dict.get(keyword, DEFAULT_LATEST_DATE)

                dr_dict   = zero_dict.copy()
                real_dict = {data.get('period'):data.get('ratio') for data in result.get('data')}
                dr_dict.update(real_dict)

                mr_dict[keyword]    = sum(list(dr_dict.values())[-30:])
                ratio_dict[keyword] = dict(filter(lambda x: x[0] > latest_date, dr_dict.items()))
            return ratio_dict, mr_dict, res_code

        except UR.HTTPError as e:
            print('Http Error:', e.code)
            return None, None, e.code

if __name__ == '__main__':
    pass
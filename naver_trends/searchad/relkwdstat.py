import hmac
import hashlib
import base64
import requests
import time as T

class RelKwdStat:
    def __init__(self, custermer_id : str, access_licence : str, secret_key : str, keyword_list=None):
        self.url            = 'https://api.naver.com/keywordstool'
        self.customer_id    = custermer_id
        self.access_licence = access_licence
        self.secret_key     = secret_key
        self.keyword_list   = keyword_list
        self.time_stamp     = int(round(T.time() * 1000))
        self.query          = self.generate_query()
        self.header         = self.generate_header()

    def generate_signature(self):
        signature = hmac.new(self.secret_key.encode(), f"{self.time_stamp}.GET./keywordstool".encode(), hashlib.sha256).digest()
        return base64.b64encode(signature).decode()

    def generate_header(self):
        return {
            'Content-Type' : 'application/json; charset=UTF-8',
            'X-Timestamp'  : str(self.time_stamp),
            'X-API-KEY'    : self.access_licence,
            'X-Customer'   : self.customer_id,
            'X-Signature'  : self.generate_signature()
        }

    def generate_query(self):
        keywords = ','.join(self.keyword_list).replace(' ', '')
        return f'?siteId={self.customer_id}&hintKeywords={keywords}&showDetail=0'

    def request(self):
        response = requests.get(f'{self.url}{self.query}', headers=self.header)
        response_code = response.status_code

        if (response_code == 200):
            click_count_dict = {keyword:[0, 0] for keyword in self.keyword_list}
            results = response.json().get('keywordList')

            for result in results:
                rel_keyword = result.get('relKeyword')
                if (rel_keyword in self.keyword_list):
                    mpc = result.get('monthlyPcQcCnt')
                    mmc = result.get('monthlyMobileQcCnt')
                    
                    if (type(mpc) is int): click_count_dict[rel_keyword][0] = mpc
                    if (type(mmc) is int): click_count_dict[rel_keyword][1] = mmc
                else:
                    break
            return click_count_dict, 200
        else:
            return None, response_code

if __name__ == '__main__':
    pass
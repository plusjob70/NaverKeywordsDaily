from abc import ABCMeta


class KeywordAnalyzer(metaclass=ABCMeta):
    def __init__(self):
        self.tag = None
        self.client_idx = 0
        self.customer_idx = 0
        self.__latest_date_dict = {}

    def get_results(self, keyword_list) -> dict:
        pass

    def get_latest_date_dict(self):
        return self.__latest_date_dict

    def set_latest_date_dict(self, latest_date_dict):
        self.__latest_date_dict = latest_date_dict

    def exceed_request_limit(self, *res_code):
        if 429 in res_code:
            print("This user has exceeded the limit of the number of requests. Requesting new user...", flush=True)
            self.client_idx += 1
            return True
        return False

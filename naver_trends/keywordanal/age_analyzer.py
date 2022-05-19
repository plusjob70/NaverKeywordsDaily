import sys
import numpy as np
from naver_trends.keywordanal.keyword_analyzer import KeywordAnalyzer
from naver_trends.datalab.keywordstrend import Keywordstrend
from naver_trends.searchad.relkwdstat_detail.relkwdstat_detail import RelkwdstatDetail
from naver_trends.common.uinfo import *
from naver_trends.common.constant import *


class AgeAnalyzer(KeywordAnalyzer):
    def __init__(self):
        super().__init__()

    def get_results(self, keyword_list):
        # initial keyword dictionary
        daily_click_dict = {keyword: {'d0c': dict, 'd13c': dict, 'd20c': dict, 'd25c': dict,
                                      'd30c': dict, 'd40c': dict, 'd50c': dict} for keyword in keyword_list}

        rel_kwd_stat = RelkwdstatDetail(CUSTOMER_LIST[self.customer_idx][UID], CUSTOMER_LIST[self.customer_idx][UPW])
        monthly_click = rel_kwd_stat.request(keyword_list, scopes=['age'])

        while True:
            try:
                keywords_trend = Keywordstrend(CLIENT_LIST[self.client_idx][ID], CLIENT_LIST[self.client_idx][SECRET])
                d0r, m0r, res_code0 = keywords_trend.request(_keyword_list=keyword_list,
                                                             _ages=['1'],
                                                             latest_date_dict=self.get_latest_date_dict().get('0-12', {}))
                d13r, m13r, res_code13 = keywords_trend.request(_keyword_list=keyword_list,
                                                                _ages=['2'],
                                                                latest_date_dict=self.get_latest_date_dict().get('13-19', {}))
                d20r, m20r, res_code20 = keywords_trend.request(_keyword_list=keyword_list,
                                                                _ages=['3'],
                                                                latest_date_dict=self.get_latest_date_dict().get('20-24', {}))
                d25r, m25r, res_code25 = keywords_trend.request(_keyword_list=keyword_list,
                                                                _ages=['4'],
                                                                latest_date_dict=self.get_latest_date_dict().get('25-29', {}))
                d30r, m30r, res_code30 = keywords_trend.request(_keyword_list=keyword_list,
                                                                _ages=['5', '6'],
                                                                latest_date_dict=self.get_latest_date_dict().get('30-39', {}))
                d40r, m40r, res_code40 = keywords_trend.request(_keyword_list=keyword_list,
                                                                _ages=['7', '8'],
                                                                latest_date_dict=self.get_latest_date_dict().get('40-49', {}))
                d50r, m50r, res_code50 = keywords_trend.request(_keyword_list=keyword_list,
                                                                _ages=['9', '10', '11'],
                                                                latest_date_dict=self.get_latest_date_dict().get('50-', {}))
                if not self.exceed_request_limit(res_code0, res_code13, res_code20, res_code25, res_code30, res_code40, res_code50):
                    break
            except IndexError:
                print('Cannot analyze : {}'.format(keyword_list))
                sys.exit('All users are exhausted')

        for keyword in keyword_list:
            for dr, mr, label, click_cnt in zip([d0r, d13r, d20r, d25r, d30r, d40r, d50r],
                                                [m0r, m13r, m20r, m25r, m30r, m40r, m50r],
                                                ['0-12', '13-19', '20-24', '25-29', '30-39', '40-49', '50-'],
                                                ['d0c', 'd13c', 'd20c', 'd25c', 'd30c', 'd40c', 'd50c']):
                date = list(dr[keyword].keys())
                ratio = np.array(list(dr[keyword].values()))

                m_constant = (monthly_click[keyword].get(label, 0) / mr[keyword]) if (monthly_click.get(keyword, None) and mr[keyword]) else 0
                click = (ratio * m_constant).astype(int)
                daily_click_dict[keyword][click_cnt] = dict(zip(date, click))

        return daily_click_dict


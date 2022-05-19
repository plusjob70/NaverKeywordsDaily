import sys
import numpy as np
from naver_trends.keywordanal.keyword_analyzer import KeywordAnalyzer
from naver_trends.datalab.keywordstrend import Keywordstrend
from naver_trends.searchad.relkwdstat_detail.relkwdstat_detail import RelkwdstatDetail
from naver_trends.common.uinfo import *
from naver_trends.common.constant import *


class GenderAnalyzer(KeywordAnalyzer):
    def __init__(self):
        super().__init__()

    """
    dmc : Daily   Male   Click
    dmr : Daily   Male   Ratio
    mmc : Monthly Male   Click
    mmr : Monthly Male   Ratio
    dfc : Daily   Female Click
    dfr : Daily   Female Ratio
    mfc : Monthly Female Click
    mfr : Monthly Female Ratio
    """
    def get_results(self, keyword_list):
        # initial keyword dictionary
        daily_click_dict = {keyword: {'dmc': dict, 'dfc': dict} for keyword in keyword_list}

        rel_kwd_stat = RelkwdstatDetail(CUSTOMER_LIST[self.customer_idx][UID], CUSTOMER_LIST[self.customer_idx][UPW])
        monthly_click = rel_kwd_stat.request(keyword_list, scopes=['gender'])

        while True:
            try:
                keywords_trend = Keywordstrend(CLIENT_LIST[self.client_idx][ID], CLIENT_LIST[self.client_idx][SECRET])
                dmr, mmr, mal_res_code = keywords_trend.request(_keyword_list=keyword_list,
                                                                _gender='m',
                                                                latest_date_dict=self.get_latest_date_dict().get('남', {}))
                dfr, mfr, fem_res_code = keywords_trend.request(_keyword_list=keyword_list,
                                                                _gender='f',
                                                                latest_date_dict=self.get_latest_date_dict().get('여', {}))
                if not self.exceed_request_limit(mal_res_code, fem_res_code):
                    break
            except IndexError:
                print('Cannot analyze : {}'.format(keyword_list))
                sys.exit('All users are exhausted')

        # calculate daily click (dmc, dfc)
        for keyword in keyword_list:
            m_date = list(dmr[keyword].keys())
            f_date = list(dfr[keyword].keys())
            m_ratio = np.array(list(dmr[keyword].values()))
            f_ratio = np.array(list(dfr[keyword].values()))

            # mm_constant = mmc / mmr
            # mf_constant = mfc / mfr
            mm_constant = (monthly_click[keyword]['m'] / mmr[keyword]) if (monthly_click[keyword] and mmr[keyword]) else 0
            mf_constant = (monthly_click[keyword]['f'] / mfr[keyword]) if (monthly_click[keyword] and mfr[keyword]) else 0

            m_click = (m_ratio * mm_constant).astype(int)
            f_click = (f_ratio * mf_constant).astype(int)

            daily_click_dict[keyword]['dmc'] = dict(zip(m_date, m_click))
            daily_click_dict[keyword]['dfc'] = dict(zip(f_date, f_click))

        return daily_click_dict

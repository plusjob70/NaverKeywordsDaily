import sys
import numpy as np
from naver_trends.keywordanal.keyword_analyzer import KeywordAnalyzer
from naver_trends.datalab.keywordstrend import Keywordstrend
from naver_trends.searchad.relkwdstat import RelKwdStat
from naver_trends.common.uinfo import *
from naver_trends.common.constant import *


class DeviceAnalyzer(KeywordAnalyzer):
    def __init__(self):
        super().__init__()

    """
    dpc : Daily   PC     Click
    dpr : Daily   PC     Ratio
    mpc : Monthly PC     Click
    mpr : Monthly PC     Ratio
    dmc : Daily   Mobile Click
    dmr : Daily   Mobile Ratio
    mmc : Monthly Mobile Click
    mmr : Monthly Mobile Ratio
    """
    def get_results(self, keyword_list) -> dict:
        # initial keyword dictionary
        daily_click_dict = {keyword: {'dpc': dict, 'dmc': dict} for keyword in keyword_list}

        rel_kwd_stat = RelKwdStat(CUSTOMER_LIST[self.customer_idx][ID],
                                  CUSTOMER_LIST[self.customer_idx][LICENSE],
                                  CUSTOMER_LIST[self.customer_idx][SECRET])
        monthly_click, _ = rel_kwd_stat.request(keyword_list)

        while True:
            try:
                keywords_trend = Keywordstrend(CLIENT_LIST[self.client_idx][ID], CLIENT_LIST[self.client_idx][SECRET])
                dpr, mpr, pc_res_code = keywords_trend.request(_keyword_list=keyword_list,
                                                               _device='pc',
                                                               latest_date_dict=self.get_latest_date_dict().get('PC', {}))
                dmr, mmr, mo_res_code = keywords_trend.request(_keyword_list=keyword_list,
                                                               _device='mo',
                                                               latest_date_dict=self.get_latest_date_dict().get('모바일', {}))
                if not self.exceed_request_limit(pc_res_code, mo_res_code):
                    break
            except IndexError:
                print('Cannot analyze : {}'.format(keyword_list))
                sys.exit('All users are exhausted')

        # calculate daily click (dpc, dmc)
        for keyword in keyword_list:
            p_date = list(dpr[keyword].keys())
            m_date = list(dmr[keyword].keys())
            p_ratio = np.array(list(dpr[keyword].values()))
            m_ratio = np.array(list(dmr[keyword].values()))

            # mp_constant = mpc / mpr
            # mm_constant = mmc / mmr
            mp_constant = (monthly_click[keyword][PC] / mpr[keyword]) if mpr[keyword] else 0
            mm_constant = (monthly_click[keyword][MO] / mmr[keyword]) if mmr[keyword] else 0

            p_click = (p_ratio * mp_constant).astype(int)
            m_click = (m_ratio * mm_constant).astype(int)

            daily_click_dict[keyword]['dpc'] = dict(zip(p_date, p_click))
            daily_click_dict[keyword]['dmc'] = dict(zip(m_date, m_click))

        return daily_click_dict

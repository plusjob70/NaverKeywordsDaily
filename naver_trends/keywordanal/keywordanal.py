import sys
import numpy as np
from naver_trends.datalab.keywordstrend import Keywordstrend
from naver_trends.searchad.relkwdstat import RelKwdStat
from naver_trends.common.uinfo import *
from naver_trends.common.constant import *

class Keywordanal:
    def __init__(self):
        self.client_idx       = 0
        self.customer_idx     = 0
        self.latest_date_dict = {}

    def get_results(self, keyword_list) -> dict:
        '''
            dpc : Daily   PC     Click
            dpr : Daily   PC     Ratio
            mpc : Monthly PC     Click
            mpr : Monthly PC     Ratio
            dmc : Daily   Mobile Click
            dmr : Daily   Mobile Ratio
            mmc : Monthly Mobile Click
            mmr : Monthly Mobile Ratio
        '''
        # initial keyword dictionary
        keyword_dict = {keyword : {'dpc':dict, 'dmc':dict} for keyword in keyword_list}

        # create Keywordstrend and relkwdstat object
        kt  = Keywordstrend(CLIENT_LIST[self.client_idx][ID], CLIENT_LIST[self.client_idx][SECRET], keyword_list)
        rks = RelKwdStat(CUSTOMER_LIST[self.customer_idx][ID], CUSTOMER_LIST[self.customer_idx][LICENSE], CUSTOMER_LIST[self.customer_idx][SECRET], keyword_list)

        # get keywords trend
        dpr, mpr, pc_res_code = kt.request(device='pc', latest_date_dict=self.latest_date_dict.get('PC', None))
        dmr, mmr, mo_res_code = kt.request(device='mo', latest_date_dict=self.latest_date_dict.get('모바일', None))
            
        while (pc_res_code == 429 | mo_res_code == 429):
            try:                                                               
                print("This user has exceeded the limit of the number of requests. Requesting new user...", flush=True)
                self.client_idx += 1
                kt = Keywordstrend(CLIENT_LIST[self.client_idx][ID], CLIENT_LIST[self.client_idx][SECRET], keyword_list)
                dpr, mpr, pc_res_code = kt.request(device='pc', latest_date_dict=self.latest_date_dict.get('PC', None))
                dmr, mmr, mo_res_code = kt.request(device='mo', latest_date_dict=self.latest_date_dict.get('모바일', None))
            except IndexError:
                print('Cannot analyze : {}'.format(keyword_list))
                sys.exit('All users are exhausted')

        # get relkwdstat
        monthly_click, _ = rks.request()

        # calculate daily click (dpc, dmc)
        for keyword in keyword_list:
            p_date  = list(dpr[keyword].keys())
            m_date  = list(dmr[keyword].keys())
            p_ratio = np.array(list(dpr[keyword].values()))
            m_ratio = np.array(list(dmr[keyword].values()))

            mp_constant = 0  # mp_constant = mpc / mpr
            mm_constant = 0  # mm_constant = mmc / mmr

            if mpr[keyword] != 0: 
                mp_constant = monthly_click[keyword][PC] / mpr[keyword]
            if mmr[keyword] != 0: 
                mm_constant = monthly_click[keyword][MO] / mmr[keyword]

            p_click = (p_ratio * mp_constant).astype(int)
            m_click = (m_ratio * mm_constant).astype(int)

            keyword_dict[keyword]['dpc'] = dict(zip(p_date, p_click))
            keyword_dict[keyword]['dmc'] = dict(zip(m_date, m_click))

        return keyword_dict
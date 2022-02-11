from naver_trends.datalab.keywordstrend import Keywordstrend
from naver_trends.searchad.relkwdstat import RelKwdStat
from naver_trends.common.uinfo import *
from naver_trends.common.constant import *

class Keywordanal:
    def __init__(self, mode:str=None):
        self.client_idx       = 0
        self.customer_idx     = 0
        self.latest_date_dict = {}

        # if gender mode then clawer is excuted
        if mode == 'gender':
            from naver_trends.searchad.crawler.crawattr import GenderCraw

            self.genCrawler = GenderCraw(CHROME_DRIVER_PATH)
            self.genCrawler.login_searchad(CUSTOMER_LIST[self.customer_idx][UID], CUSTOMER_LIST[self.customer_idx][UPW], CUSTOMER_LIST[self.customer_idx][ID])

    def get_keyword_anal_results(self, keyword_list) -> dict:
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
                print('All users are exhausted', flush=True)
                print('Cannot analyze : {}'.format(keyword_list))
                exit()

        # get relkwdstat
        monthly_click, _ = rks.request()

        # calculate daily click (dpc, dmc)
        for keyword in keyword_list:
            p_date  = list(dpr[keyword].keys())
            m_date  = list(dmr[keyword].keys())
            p_ratio = list(dpr[keyword].values())
            m_ratio = list(dmr[keyword].values())

            mp_constant = 0  # mp_constant = mpc / mpr
            mm_constant = 0  # mm_constant = mmc / mmr

            if mpr[keyword] != 0:
                mp_constant = monthly_click[keyword][PC] / mpr[keyword]
            if mmr[keyword] != 0:
                mm_constant = monthly_click[keyword][MO] / mmr[keyword]

            p_click = list(map(lambda dpr: int(mp_constant * dpr), p_ratio))
            m_click = list(map(lambda dmr: int(mm_constant * dmr), m_ratio))

            keyword_dict[keyword]['dpc'] = dict(zip(p_date, p_click))
            keyword_dict[keyword]['dmc'] = dict(zip(m_date, m_click))

        return keyword_dict
    
    def get_gender_keyword_anal_results(self, keyword_list) -> dict:
        '''
            dmc : Daily   Men   Click
            dwc : Daily   Women Click
            dmr : Daily   Men   Ratio
            dwr : Daily   Women Ratio
            mmr : Monthly Men   Ratio
            mwr : Monthly Women Ratio
            mmc : Monthly Men   Click
            mwc : Monthly Women Click
        '''
        # initial keyword dictionary & 
        # Monthly gender click dictionary--{'keyword' : [Men_click, Women_click]}
        keyword_dict = {keyword : {'dmc':dict, 'dwc':dict} for keyword in keyword_list}
        mgc_dict     = {keyword : [0, 0] for keyword in keyword_list}
        
        # create Keywordstrend and relkwdstat object
        kt  = Keywordstrend(CLIENT_LIST[self.client_idx][ID], CLIENT_LIST[self.client_idx][SECRET], keyword_list)
        rks = RelKwdStat(CUSTOMER_LIST[self.customer_idx][ID], CUSTOMER_LIST[self.customer_idx][LICENSE], CUSTOMER_LIST[self.customer_idx][SECRET], keyword_list)

        # get keywords trend
        dmr, mmr, men_res_code = kt.request(gender='m', latest_date_dict=self.latest_date_dict.get('남', None))
        dwr, mwr, wom_res_code = kt.request(gender='f', latest_date_dict=self.latest_date_dict.get('여', None))

        while (men_res_code == 429 | wom_res_code == 429):
            try:                                                               
                print("This user has exceeded the limit of the number of requests. Requesting new user...", flush=True)
                self.client_idx += 1
                kt = Keywordstrend(CLIENT_LIST[self.client_idx][ID], CLIENT_LIST[self.client_idx][SECRET], keyword_list)
                dmr, mmr, men_res_code = kt.request(gender='m', latest_date_dict=self.latest_date_dict.get('남', None))
                dwr, mwr, wom_res_code = kt.request(gender='f', latest_date_dict=self.latest_date_dict.get('여', None))
            except IndexError:
                print('All users are exhausted', flush=True)
                print('Cannot analyze : {}'.format(keyword_list))
                exit()

        # get relkwdstat
        monthly_click, _ = rks.request()

        # get gender ratio using Clawer
        gender_ratio_dict = self.genCrawler.extract_relkwd_info(keyword_list)
        
        # calculate gender click
        for keyword, click_count in monthly_click.items():            
            pc_men_click = int(gender_ratio_dict[keyword]['PC']['m'] * click_count[PC])
            mo_men_click = int(gender_ratio_dict[keyword]['모바일']['m'] * click_count[MO])

            pc_wom_click = click_count[PC] - pc_men_click
            mo_wom_click = click_count[MO] - mo_men_click

            mgc_dict[keyword][MEN] = pc_men_click + mo_men_click
            mgc_dict[keyword][WOM] = pc_wom_click + mo_wom_click

        # calculate daily click (dmc, dwc)
        for keyword in keyword_list:
            m_date  = list(dmr[keyword].keys())
            w_date  = list(dwr[keyword].keys())
            m_ratio = list(dmr[keyword].values())
            w_ratio = list(dwr[keyword].values())

            mm_constant = 0  # mm_constant = mmc / mmr
            mw_constant = 0  # mw_constant = mwc / mwr

            if mmr[keyword] != 0:
                mm_constant = mgc_dict[keyword][MEN] / mmr[keyword]   
            if mwr[keyword] != 0:
                mw_constant = mgc_dict[keyword][WOM] / mwr[keyword]

            m_click = list(map(lambda dmr: int(mm_constant * dmr), m_ratio))
            w_click = list(map(lambda dwr: int(mw_constant * dwr), w_ratio))

            keyword_dict[keyword]['dmc'] = dict(zip(m_date, m_click))
            keyword_dict[keyword]['dwc'] = dict(zip(w_date, w_click))

        return keyword_dict

if __name__ == '__main__':
    pass
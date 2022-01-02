from datalab.keywordstrend import Keywordstrend
from searchad.relkwdstat import RelKwdStat
from common.uinfo import *
from common.constant import *

class Keywordanal:
    def __init__(self):
        self.client_idx   = 0
        self.customer_idx = 0

    def list_to_dict(self, keyword_list, latest_date_dict={}) -> dict:
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
        keyword_dict = {keyword : {'mpc':int, 'mmc':int, 'mpr':float, 'mmr':float, 'dpc':dict, 'dmc':dict} for keyword in keyword_list}

        # create Keywordstrend and relkwdstat object
        kt  = Keywordstrend(CLIENT_LIST[self.client_idx][ID], CLIENT_LIST[self.client_idx][SECRET], keyword_list)
        rks = RelKwdStat(CUSTOMER_LIST[self.customer_idx][ID], CUSTOMER_LIST[self.customer_idx][LICENSE], CUSTOMER_LIST[self.customer_idx][SECRET], keyword_list)

        # get keywords trend
        dpc, mpr, pc_res_code = kt.request(device='pc', latest_date_dict=latest_date_dict.get('pc', None))
        dmc, mmr, mo_res_code = kt.request(device='mo', latest_date_dict=latest_date_dict.get('mo', None))
            
        while (pc_res_code == 429 | mo_res_code == 429):
            try:
                print("This user has exceeded the limit of the number of requests. Requesting new user...")
                self.client_idx += 1
                kt = Keywordstrend(CLIENT_LIST[self.client_idx][ID], CLIENT_LIST[self.client_idx][SECRET], keyword_list)
                dpc, mpr, pc_res_code = kt.request(device='pc', latest_date_dict=latest_date_dict.get('pc', None))
                dmc, mmr, mo_res_code = kt.request(device='mo', latest_date_dict=latest_date_dict.get('mo', None))
            except IndexError:
                print('All users are exhausted')
                print('Cannot analyze : {}'.format(keyword_list))
                exit()

        # get relkwdstat
        monthly_click, _ = rks.request()

        for keyword in keyword_list:
            keyword_dict[keyword]['dpc'], keyword_dict[keyword]['dmc'] = dpc[keyword],  dmc[keyword]
            keyword_dict[keyword]['mpr'], keyword_dict[keyword]['mmr'] = mpr[keyword],  mmr[keyword]

            keyword_dict[keyword]['mpc'] = monthly_click[keyword][PC]
            keyword_dict[keyword]['mmc'] = monthly_click[keyword][MO]

        # calculate daily click (dpc, dmc)
        for keyword in keyword_list:
            mpc,      mmc      = keyword_dict[keyword]['mpc'],                keyword_dict[keyword]['mmc']
            mpr,      mmr      = keyword_dict[keyword]['mpr'],                keyword_dict[keyword]['mmr']
            dpr_list, dmr_list = list(keyword_dict[keyword]['dpc'].values()), list(keyword_dict[keyword]['dmc'].values()) 

            dpc = [int(dpr * mpc / mpr) for dpr in dpr_list] if (mpr != 0) else [0 for _ in dpr_list]
            dmc = [int(dmr * mmc / mmr) for dmr in dmr_list] if (mmr != 0) else [0 for _ in dmr_list]

            keyword_dict[keyword]['dpc'] = dict(zip(list(keyword_dict[keyword]['dpc'].keys()), dpc))
            keyword_dict[keyword]['dmc'] = dict(zip(list(keyword_dict[keyword]['dmc'].keys()), dmc))

        return keyword_dict
        
if __name__ == '__main__':
    pass
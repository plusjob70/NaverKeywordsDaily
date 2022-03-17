from naver_trends.keywordanal.keywordanal import *
from naver_trends.searchad.crawler.crawattr import GenderCraw


class Genderanal(Keywordanal):
    def __init__(self):
        super().__init__()
        self.genCrawler = GenderCraw(CHROME_DRIVER_PATH)
        self.genCrawler.login_searchad(
           CUSTOMER_LIST[self.customer_idx][UID],
           CUSTOMER_LIST[self.customer_idx][UPW],
           CUSTOMER_LIST[self.customer_idx][ID]
        )

    def get_results(self, keyword_list) -> dict:
        """
            dmc : Daily   Men   Click
            dwc : Daily   Women Click
            dmr : Daily   Men   Ratio
            dwr : Daily   Women Ratio
            mmr : Monthly Men   Ratio
            mwr : Monthly Women Ratio
            mmc : Monthly Men   Click
            mwc : Monthly Women Click
        """
        # initial keyword dictionary & 
        # Monthly gender click dictionary--{'keyword' : [Men_click, Women_click]}
        keyword_dict = {keyword: {'dmc': dict, 'dwc': dict} for keyword in keyword_list}
        mgc_dict = {keyword: [0, 0] for keyword in keyword_list}

        # create Keywordstrend and relkwdstat object
        kt = Keywordstrend(CLIENT_LIST[self.client_idx][ID],
                           CLIENT_LIST[self.client_idx][SECRET], keyword_list)
        rks = RelKwdStat(CUSTOMER_LIST[self.customer_idx][ID],
                         CUSTOMER_LIST[self.customer_idx][LICENSE],
                         CUSTOMER_LIST[self.customer_idx][SECRET], keyword_list)

        # get keywords trend
        dmr, mmr, men_res_code = kt.request(gender='m', latest_date_dict=self.latest_date_dict.get('남', None))
        dwr, mwr, wom_res_code = kt.request(gender='f', latest_date_dict=self.latest_date_dict.get('여', None))

        while men_res_code == 429 | wom_res_code == 429:
            try:
                print("This user has exceeded the limit of the number of requests. Requesting new user...", flush=True)
                self.client_idx += 1
                kt = Keywordstrend(CLIENT_LIST[self.client_idx][ID], CLIENT_LIST[self.client_idx][SECRET], keyword_list)
                dmr, mmr, men_res_code = kt.request(gender='m', latest_date_dict=self.latest_date_dict.get('남', None))
                dwr, mwr, wom_res_code = kt.request(gender='f', latest_date_dict=self.latest_date_dict.get('여', None))
            except IndexError:
                print('Cannot analyze : {}'.format(keyword_list))
                sys.exit('All users are exhausted')

        # get relkwdstat
        monthly_click, _ = rks.request()

        # get gender ratio using Crawler
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
            m_date = list(dmr[keyword].keys())
            w_date = list(dwr[keyword].keys())
            m_ratio = np.array(list(dmr[keyword].values()))
            w_ratio = np.array(list(dwr[keyword].values()))

            mm_constant = 0  # mm_constant = mmc / mmr
            mw_constant = 0  # mw_constant = mwc / mwr

            if mmr[keyword] != 0:
                mm_constant = mgc_dict[keyword][MEN] / mmr[keyword]
            if mwr[keyword] != 0:
                mw_constant = mgc_dict[keyword][WOM] / mwr[keyword]

            m_click = (m_ratio * mm_constant).astype(int)
            w_click = (w_ratio * mw_constant).astype(int)

            keyword_dict[keyword]['dmc'] = dict(zip(m_date, m_click))
            keyword_dict[keyword]['dwc'] = dict(zip(w_date, w_click))

        return keyword_dict

from naver_trends.searchad.crawler.crawler import Crawler

class GenderCraw(Crawler):
    def extract_relkwd_info(self, keyword_list):
        self.clear_input_box()
        
        keyword_str = '\n'.join(keyword_list)

        self.insert_to_input_box(keyword_str)
        self.click_search_button(keyword_list[0])

        gender_ratio_dict = {keyword:{'PC':{'m':0, 'w':0}, '모바일':{'m':0, 'w':0}} for keyword in keyword_list}

        for keyword in keyword_list:
            exist_low_search_tag = self.click_keyword_link(keyword)

            if not exist_low_search_tag:
                pc_ratio, mo_ratio = self.extract_gender_ratio()
                gender_ratio_dict[keyword]['PC'].update(pc_ratio)
                gender_ratio_dict[keyword]['모바일'].update(mo_ratio)

                self.close_keyword_info_window()
            else:
                continue
            
        self.clear_input_box()
        return gender_ratio_dict

class AgeCraw(Crawler):
    def extract_relkwd_info(self):
        pass

class GenAgeCraw(Crawler):
    def extract_relkwd_info(self):
        pass



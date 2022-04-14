import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


class Crawler:
    def __init__(self, chrome_driver_path):
        self.browser = None
        self.timer = None
        self.keyword_input_box = None
        self.search_button = None
        try:
            self.browser = webdriver.Chrome(chrome_driver_path)
            self.timer = WebDriverWait(self.browser, timeout=10, poll_frequency=0.3)
        except WebDriverException:
            print('web driver exception -- path : {}'.format(chrome_driver_path), flush=True)
            exit()

    def login_searchad(self, uid, upw, customer_id):
        try:
            self.browser.get(
                'https://searchad.naver.com/login?returnUrl=https://manage.searchad.naver.com&amp;returnMethod=get')
            self.browser.maximize_window()

            uid_input = self.browser.find_element(By.ID, 'uid')
            upw_input = self.browser.find_element(By.ID, 'upw')
            login_btn = self.browser.find_element(By.XPATH, "//button[contains(text(), '검색광고 아이디로 로그인')]")

            uid_input.send_keys(uid)
            upw_input.send_keys(upw)
            login_btn.click()

            self.timer.until(lambda x: x.find_element(By.ID, 'Tooltip-CAMPAIGNdON_OFF'))
            self.browser.get(f'https://manage.searchad.naver.com/customers/{customer_id}/tool/keyword-planner')
            self.timer.until(lambda x: x.find_element(By.ID, 'Tooltip-KEYWORD_PLANNERdKEYWORD_RELATIONAL'))
            self.keyword_input_box = self.browser.find_element(By.XPATH, "//textarea[@rows='5']")
            self.search_button = self.browser.find_element(By.XPATH, "//button/span[text()='조회하기']")
            return True
        except:
            return False

    def clear_input_box(self):
        if self.keyword_input_box is not None:
            self.keyword_input_box.clear()
            return

    def insert_to_input_box(self, keyword_str):
        if self.keyword_input_box is not None:
            self.keyword_input_box.send_keys(keyword_str)
            return

    def click_search_button(self, first_keyword):
        if self.search_button is not None:
            self.search_button.click()
            self.timer.until(lambda x: x.find_element(By.XPATH, f"//td[@data-value='{first_keyword}']"))
            return

    # if low search volume then return True
    # else return False
    def click_keyword_link(self, keyword):
        try:
            self.browser.find_element(By.XPATH, f"//td[@data-value='{keyword}']/div/span[@id='low-search-volume']")
            return True
        except NoSuchElementException:
            self.browser.find_element(By.XPATH, f"//td[@data-value='{keyword}']/div/span[@class='planner']").click()
            self.timer.until(lambda x: x.find_element(By.XPATH, "//*[name()='path'][@class='highcharts-point']"))
            return False

    def close_keyword_info_window(self):
        try:
            self.browser.find_element(By.CLASS_NAME, "btn_close").click()
        except NoSuchElementException:
            print("")

    @property
    def extract_gender_ratio(self):
        try:
            pc_men_element = self.browser.find_element(By.XPATH,
                                                       "//*[name()='g'][@class='highcharts-series highcharts-series-0 highcharts-column-series highcharts-tracker']/*[name()='rect'][@x='34.5' and @width='37']")
            mo_men_element = self.browser.find_element(By.XPATH,
                                                       "//*[name()='g'][@class='highcharts-series highcharts-series-1 highcharts-column-series highcharts-tracker']/*[name()='rect'][@x='80.5' and @width='37']")
        except NoSuchElementException:
            time.sleep(1)
            pc_men_element = self.browser.find_element(By.XPATH,
                                                       "//*[name()='g'][@class='highcharts-series highcharts-series-0 highcharts-column-series highcharts-tracker']/*[name()='rect'][(@x='31.5' and @width='19') or (@x='32.5' and @width='19') or (@x='30.5' and @width='6')]")
            mo_men_element = self.browser.find_element(By.XPATH,
                                                       "//*[name()='g'][@class='highcharts-series highcharts-series-1 highcharts-column-series highcharts-tracker']/*[name()='rect'][(@x='47.5' and @width='19') or (@x='55.5' and @width='19') or (@x='37.5' and @width='6')]")

        # idx 0 : PC / idx 1 : 모바일
        gender_ratio_dict_list = [{'m': 0, 'w': 0}, {'m': 0, 'w': 0}]

        for idx, element in enumerate([pc_men_element, mo_men_element]):
            ActionChains(self.browser).move_to_element(element).perform()

            try:
                num_click = self.browser.find_element(By.XPATH,
                                                      "/html/body/div[4]/div/div[1]/div/div/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div/div/span/div/table/tbody/tr/td[2]/strong").text
            except StaleElementReferenceException:
                num_click = self.browser.find_element(By.XPATH,
                                                      "/html/body/div[4]/div/div[1]/div/div/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div/div/span/div/table/tbody/tr/td[2]/strong").text
            except NoSuchElementException:
                try:
                    time.sleep(1)
                    num_click = self.browser.find_element(By.XPATH,
                                                          "/html/body/div[4]/div/div[1]/div/div/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div/div/span/div/table/tbody/tr/td[2]/strong").text
                except NoSuchElementException:
                    continue

            if type(num_click) is str:
                num_click = round(float(num_click) * 0.01, 4)
                gender_ratio_dict_list[idx]['m'] = num_click
                gender_ratio_dict_list[idx]['w'] = round(1 - num_click, 4)
            else:
                print(f'{element} is not str type', flush=True)

        return gender_ratio_dict_list[0], gender_ratio_dict_list[1]

    def __del__(self):
        self.browser.quit()
        return

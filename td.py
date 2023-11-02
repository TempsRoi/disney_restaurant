# coding:utf-8
import yaml
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from time import sleep
import json
import datetime
import calendar
from selenium.webdriver.chrome.service import Service
 
class RestaurantMonitor:
    def __init__(self, config_file='visit.json', restaurant_file='restaurant.txt'):
        self.config = self.load_config(config_file)
        self.restaurant_list, self.restaurant_data = self.load_restaurant_data(restaurant_file)
        self.driver = None
    
    @staticmethod
    def load_config(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def load_restaurant_data(restaurant_file):
        with open(restaurant_file, "r") as f:
            lines = f.read().splitlines()
        restaurant_data = {line.split(' ')[1]: line.split(' ')[0] for line in lines}
        return list(restaurant_data.keys()), restaurant_data
    
    @staticmethod
    def send_line_notify(notification_message, line_notify_token):
        line_notify_api = 'https://notify-api.line.me/api/notify'
        headers = {'Authorization': f'Bearer {line_notify_token}'}
        data = {'message': f'{notification_message}'}
        requests.post(line_notify_api, headers=headers, data=data)

    def start_browser(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        executable_path='/usr/lib/chromium-browser/chromedriver'
        service = Service(executable_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(120)  # タイムアウトを60秒に設定
    def close_browser(self):
        if self.driver:
            self.driver.quit()

    def monitor(self):
        try:
            self.start_browser()
            # 予約トップページへ遷移
            print("予約トップページへ遷移")
            self.driver.get("https://www.google.co.jp/")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'searchUseDateDisp')))
            print("aaa")
            sleep(3)

            # 日付の指定
            print("日付の指定")
            date_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'searchUseDateDisp')))
            date_input.send_keys(self.config["date"])
            

#            # "レストラン"のイメージリンクをクリック
#            print("レストランのイメージリンクをクリック")
#            self.driver.find_element_by_xpath("//img[@src='/cgp/images/jp/pc/btn/btn_gn_04.png']").click();
#            sleep(3)
#
#            # 同意書の同意ボタンをクリック
#            print("同意書の同意ボタンをクリック")
#            self.driver.find_element_by_xpath("//img[@src='/cgp/images/jp/pc/btn/btn_close_08.png']").click();
#            self.driver.implicitly_wait(3)

            # 日付の指定
            print("日付の指定")
            self.driver.find_element_by_id('searchUseDateDisp').send_keys(self.config["date"])

            # 人数の指定
            print("人数の指定")
            color_element = self.driver.find_element_by_id('searchAdultNum')
            color_select_element = Select(color_element)
            color_select_element.select_by_value(str(self.config["adult"]))

            # レストランの指定
            print("レストランの指定")
            color_element = self.driver.find_element_by_id('nameCd')
            color_select_element = Select(color_element)
            color_select_element.select_by_value(self.restaurant_data[self.config["restaurant"]])

            # "検索する"をクリック
            print("検索するをクリック")
            self.driver.find_element_by_xpath("//input[@src='/cgp/images/jp/pc/btn/btn_search_01.png']").click();
            sleep(1)

            # ページのスクロール
            print("ページのスクロール")
            height = self.driver.execute_script("return document.body.scrollHeight")
            for x in range(1, height):
                self.driver.execute_script("window.scrollTo(0, " + str(x) + ");")
            sleep(3)

            # 検索結果から空き状況を判定
            print("検索結果から空き状況を判定")
            if "お探しの条件で、空きはございません。" in self.driver.find_element_by_id('hasNotResultDiv').text:
                print(self.driver.find_element_by_id('hasNotResultDiv').text)
            else:
                print("空きが見つかりました")
                self.send_line_notify('空きが出ました\n', self.config['line_notify_token'])
        
        except Exception as e:
            print("エラーが発生しました:", e)
        
        finally:
            self.close_browser()

    def run(self):
        while True:
            self.monitor()
            sleep(int(self.config["interval"].replace("分", "")) * 60)

if __name__ == "__main__":
    monitor = RestaurantMonitor()
    monitor.run()


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.common import exceptions
from pprint import pprint
import json
from pymongo import MongoClient, errors, ASCENDING
import itertools
from collections import defaultdict

# 2) Написать программу, которая собирает «Новинки» с сайта техники mvideo и складывает данные в БД.
# Сайт можно выбрать и свой. Главный критерий выбора: динамически загружаемые товары

client = MongoClient('127.0.0.1', 27017)
db = client['Library']
mvideo_db = db.mvideo


chrome_options = Options()
chrome_options.add_argument('start-maximized')
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument('disable-infobars')
chrome_options.add_argument('--disable-extensions')


driver = webdriver.Chrome(executable_path='/Users/annazaytseva/Documents/python_parsing/chromedriver')

driver.get('https://www.mvideo.ru/')

TIME_TIMEOUT = 20

town = WebDriverWait(driver, TIME_TIMEOUT).until(EC.presence_of_element_located(
    (By.XPATH, '//a[contains(@class, "c-btn geolocation__action-approve-city")]')))
town.click()


news_block = driver.find_element_by_xpath('//h2[contains(text(), "Новинки")]/../../following-sibling::div')
actions = ActionChains(driver)
actions.move_to_element(news_block)
actions.perform()

while True:
    try:
        next_button = WebDriverWait(news_block, TIME_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[class="next-btn c-btn c-btn_scroll-horizontal c-btn_icon i-icon-fl-arrow-right"]')))
        time.sleep(1)
        next_button.click()
    except exceptions.TimeoutException:
        break

name = news_block.find_elements_by_css_selector('a.fl-product-tile-title__link')
price = news_block.find_elements_by_css_selector('span[itemprop="price"]')

mvideo_list_1 = []


def parser_name(data):
    i = 0
    for el in data:
        mvideo_data = {}
        mvideo_data['id'] = i
        mvideo_data['name'] = el.get_attribute('text').replace('\n', '').replace('  ', '')
        mvideo_data['link'] = el.get_attribute('href')
        mvideo_list_1.append(mvideo_data)
        i += 1
    return mvideo_list_1


mvideo_list_2 = []


def parser_price(data):
    i = 0
    for el in data:
        mvideo_data = {}
        mvideo_data['id'] = i
        mvideo_data['price'] = int(el.get_attribute('innerHTML').replace('\n', '').replace(
            '\t', '').replace('&nbsp;', ' ').replace(' ', '').replace('₽', '').split('<')[0])
        mvideo_list_2.append(mvideo_data)
        i += 1
    return mvideo_list_2


parser_name(name)
parser_price(price)

temp_data = defaultdict(dict)
for item in itertools.chain(mvideo_list_1, mvideo_list_2):
    temp_data[item['id']].update(item)

data = list(temp_data.values())

driver.quit()

# print(len(data))
# pprint(data)

with open('mvideo_json.json', 'w') as f:
    json.dump(data, f)

for i in data:
    mvideo_db.insert_one(i)

# for i in mvideo_db.find():
#     pprint(i)

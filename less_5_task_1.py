from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from selenium.common import exceptions
from pprint import pprint
import json
from pymongo import MongoClient, errors, ASCENDING

# 1) Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные о
# письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172!!!

client = MongoClient('127.0.0.1', 27017)
db = client['Library']
letters_db = db.letters


chrome_options = Options()
chrome_options.add_argument('start-maximized')
chrome_options.add_argument('disable-infobars')
chrome_options.add_argument('--disable-extensions')

driver = webdriver.Chrome(executable_path='/Users/annazaytseva/Documents/python_parsing/chromedriver')

driver.get('https://account.mail.ru/login?page=https%3A%2F%2Fe.mail.ru%2Fmessages%2Finbox%3Futm_source%3Dportal'
           '%26utm_medium%3Dportal_navigation%26utm_campaign%3De.mail.ru%26mt_sub3%3D90862077%26mt_sub4%3D413305'
           '%26mt_sub5%3D169%26mt_sub1%3Dmail.ru%26mt_click_id%3Dmt-rl95z4-1630349299-3888846517&allow_external=1'
           '&from=octavius')

TIME_TIMEOUT = 20

login = WebDriverWait(driver, TIME_TIMEOUT).until(EC.presence_of_element_located((By.NAME, 'username')))
login.send_keys('study.ai_172@mail.ru')
login.send_keys(Keys.ENTER)

password = WebDriverWait(driver, TIME_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '//input['
                                                                                               '@name="password"]')))
time.sleep(1)
password.send_keys('NextPassword172!!!')
password.send_keys(Keys.ENTER)

first_letter = WebDriverWait(driver, TIME_TIMEOUT).until(
    EC.presence_of_element_located((By.XPATH, '//a[contains(@class, "js-letter-list-item llc_normal")]')))
first_letter.click()

letters_list = []


def pars_letters(el):
    letters_data = {'from': WebDriverWait(el, TIME_TIMEOUT).until(
        EC.presence_of_element_located((By.XPATH, '//span[contains(@class, "letter-contact")]'))).text,
                    'date': WebDriverWait(el, TIME_TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "letter__date")]'))).text,
                    'subject': WebDriverWait(el, TIME_TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, '//h2[contains(@class, "thread__subject")]'))).text,
                    'text_messege': WebDriverWait(el, TIME_TIMEOUT).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.letter-body__body'))).text}
    letters_list.append(letters_data)
    letters_db.insert_one(letters_data)

    return letters_list


count = 0
while count < 10:
    try:
        time.sleep(0.5)
        pars_letters(driver)
        button_next = WebDriverWait(driver, TIME_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, '//span[@data-title-shortcut="Ctrl+K"]')))
        button_next.click()
        count += 1
    except exceptions.TimeoutException:
        print('E-mails are over')
        break

# pprint(letters_list)
driver.quit()

for uniq in letters_list:
    try:
        uniq.pop('_id')
    except:
        continue

with open('news_json.json', 'w') as f:
    json.dump(letters_list, f)

# for i in letters_db.find():
#     pprint(i)

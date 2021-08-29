from lxml import html
import requests
from pprint import pprint
import json
from pymongo import MongoClient, errors, ASCENDING

# 1. Написать приложение, которое собирает основные новости с сайта на выбор lenta.ru, news.mail.ru, yandex-новости.
# Для парсинга использовать XPath. Структура данных должна содержать:
# название источника (srs);
# наименование новости (name);
# ссылку на новость (link);
# дата публикации (date).
# 2. Сложить собранные данные в БД


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/92.0.4515.159 Safari/537.36'}

client = MongoClient('127.0.0.1', 27017)
db = client['Library']
news_db = db.news
news_db.create_index([('link', ASCENDING)], unique=True)

news_list_lent = []


def search_news_lent(url):
    response = requests.get(url, headers=headers)
    if response.ok:
        dom = html.fromstring(response.text)
        item = dom.xpath(".//div[contains(@class, 'b-longgrid-column')]/div[contains(@class, 'item')]")
        for v in item:
            news_data = {}
            name = v.xpath('.//h3/a/text()')
            for i in name:
                i = i.replace(u'\xa0', u' ')
                i = i.replace(u'\u202f', u' ')
                news_data['name'] = i
            link = v.xpath('.//h3/a/@href')
            srs = v.xpath('.//h3/a/text()')
            for i in srs:
                news_data['srs'] = 'https://lenta.ru/parts' + i
            for i in link:
                news_data['link'] = 'https://lenta.ru/parts' + i
            news_data['data'] = v.xpath('.//div[@class="info g-date item__info"]/text()')
            news_data['website'] = 'https://lenta.ru/'

            news_list_lent.append(news_data)
            try:
                news_db.insert_one(news_data)
            except errors.DuplicateKeyError:
                continue

    return news_list_lent


news_list_mail = []


def search_news_mail(url):
    response = requests.get(url, headers=headers)
    if response.ok:
        dom = html.fromstring(response.text)
        item = dom.xpath(".//a[contains(@class, 'newsitem__title')] | "
                         ".//li[contains(@class, 'list__item')] | "
                         ".//div[contains(@class, 'daynews__item')][1] | "
                         ".//div[contains(@class, 'daynews__item')][2]")
        for v in item:
            news_data = {}
            name = v.xpath(".//span[contains(@class, 'list__text')]/a/span/text() | "
                           ".//a[contains(@class, 'list__text')]/text() | "
                           ".//span[contains(@class, 'js-topnews__notification')]/text() | "
                           ".//span[contains(@class, 'newsitem__title-inner')]/text()")
            for i in name:
                i = i.replace(u'\xa0', u' ')
                i = i.replace(u'\u202f', u' ')
                news_data['name'] = i

            link = v.xpath(".//span[contains(@class, 'list__text')]/a/@href | "
                           ".//a[contains(@class, 'list__text')]/@href | "
                           ".//a[contains(@class, 'js-topnews__item')]/@href | "
                           ".//@href")
            news_data['link'] = link
            for item in link:
                response_link = requests.get(item, headers=headers)
                dom_link = html.fromstring(response_link.text)
                news_data['srs'] = dom_link.xpath(".//div[contains(@class, 'breadcrumbs')]/span[2]/span/a/span/text()")
                news_data['date'] = dom_link.xpath(".//div[contains(@class, 'breadcrumbs')]/span[1]/span/span/text()")

            news_data['website'] = 'https://news.mail.ru/'

            news_list_mail.append(news_data)
            try:
                news_db.insert_one(news_data)
            except errors.DuplicateKeyError:
                continue

    return news_list_mail


news_list_ya = []


def search_news_ya(url):
    response = requests.get(url, headers=headers)
    if response.ok:
        dom = html.fromstring(response.text)
        item = dom.xpath(
            ".//article[contains(@class, 'mg-grid__item')]")
        for v in item:
            news_data = {}
            name = v.xpath(".//a[contains(@class, 'mg-card__link')]/h2/text()")
            for i in name:
                i = i.replace(u'\xa0', u' ')
                i = i.replace(u'\u202f', u' ')
                news_data['name'] = i

            news_data['link'] = v.xpath(".//a[contains(@class, 'mg-card__link')]/@href")
            news_data['srs'] = 'Lenta.Ru'
            news_data['data'] = v.xpath(".//span[contains(@class, 'mg-card-source__time')]/text()")
            news_data['website'] = 'https://yandex.ru/news/'

            news_list_ya.append(news_data)
            try:
                news_db.insert_one(news_data)
            except errors.DuplicateKeyError:
                continue

    return news_list_ya


url_lent = 'https://lenta.ru/parts/news/'
url_mail = 'https://news.mail.ru/'
url_ya = 'https://yandex.ru/news/'

lent = search_news_lent(url_lent)

mail = search_news_mail(url_mail)

ya = search_news_ya(url_ya)

news_list = lent + mail + ya


for uniq in news_list:
    try:
        uniq.pop('_id')
    except:
        continue

with open('news_json.json', 'w') as f:
    json.dump(news_list, f)

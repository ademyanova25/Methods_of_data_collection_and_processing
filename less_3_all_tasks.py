from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import json
import re
from pymongo import MongoClient, errors, ASCENDING

# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
# записывающую собранные вакансии в созданную БД. (ниже в функциях по сбору)

# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
# (ниже create_index и в функциях по сбору (try/exception))

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                         'Version/14.1 Safari/605.1.15'}

client = MongoClient('127.0.0.1', 27017)
db = client['Library']
vacancy_db = db.vacancy
vacancy_db.create_index([('link', ASCENDING)], unique=True)


# Функции по сбору вакансий

vacancy_list_hh = []
# url - ссылка, position - должность, max_page - кол-во страниц, sal - желаемая зп


def search_vacancy_hh(url, position, max_page, sal):
    params = {'st': 'searchVacancy',
                 'text': None,
                 'area': '1',
                 'salary': sal,
                 'currency_code': 'RUR',
                 'no_magic': 'true',
                 'L_save_area': 'true',
                 'page': None}
    page_list = list(range(1, max_page+1))
    for a in position:
        params['text'] = a
        for b in page_list:
            params['page'] = b
            response = requests.get(url + 'search/vacancy', params=params, headers=headers)
            if response.ok:
                soup = bs(response.text, 'html.parser')
                vacancy = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})
                for v in vacancy:
                    vacancy_data = {}
                    info = v.find('a', attrs={'class': 'bloko-link'})
                    vacancy_data['name'] = info.getText()
                    vacancy_data['link'] = info['href']
                    vacancy_data['employer'] = v.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).getText().replace(u'\xa0', u'')
                    try:
                        salary = v.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).getText()
                        if not salary:
                            salary_min = None
                            salary_max = None
                        else:
                            salary = salary.replace(u'\xa0', u'')
                            salary = salary.replace(u'\u202f', u'')
                            slr = salary.split('–')
                            slr[0] = re.sub(r'[^0-9]', '', slr[0])
                            salary_min = int(slr[0])
                            if len(slr) > 1:
                                slr[1] = re.sub(r'[^0-9]', '', slr[1])
                                salary_max = int(slr[1])
                            else:
                                salary_max = salary_min
                        vacancy_data['salary_min'] = salary_min
                        vacancy_data['salary_max'] = salary_max
                    except:
                        vacancy_data['salary_min'] = None
                        vacancy_data['salary_max'] = None

                    vacancy_data['website'] = 'https://hh.ru/'

                    vacancy_list_hh.append(vacancy_data)
                    try:
                        vacancy_db.insert_one(vacancy_data)
                    except errors.DuplicateKeyError:
                        continue
            else:
                break

    return vacancy_list_hh


vacancy_list_sj = []
# url - ссылка, position - должность, max_page - кол-во страниц, sal - желаемая зп


def search_vacancy_sj(url, position, max_page, sal):
    params = {
        'keywords': None,
        'page': None,
        'payment_value': sal
    }

    page_list = list(range(1, max_page+1))
    for a in position:
        params['keywords'] = a
        for b in page_list:
            params['page'] = b
            response = requests.get(url + '/vacancy/search/', params=params, headers=headers)
            if response.ok:
                soup = bs(response.text, 'html.parser')
                vacancy = soup.find_all('div', attrs={'class': 'f-test-vacancy-item'})
                for v in vacancy:
                    vacancy_data = {}
                    vacancy_data['name'] = v.find('div', attrs={'class': '_21a7u'}).getText()
                    vacancy_data['link'] = url + v.find('a', attrs={'class': '_1UJAN'})['href']
                    try:
                        vacancy_data['employer'] = v.find('span', attrs={
                            'class': 'f-test-text-vacancy-item-company-name'}).getText()
                    except:
                        vacancy_data['employer'] = None
                    try:
                        salary = v.find('span', attrs={'class': 'f-test-text-company-item-salary'}).getText()
                        if not salary:
                            salary_min = None
                            salary_max = None
                        else:
                            salary = salary.replace(u'\xa0', u'')
                            salary = salary.replace(u'\u202f', u'')
                            slr = salary.split('—')
                            slr[0] = re.sub(r'[^0-9]', '', slr[0])
                            salary_min = int(slr[0])
                            if len(slr) > 1:
                                slr[1] = re.sub(r'[^0-9]', '', slr[1])
                                salary_max = int(slr[1])
                            else:
                                salary_max = salary_min
                        vacancy_data['salary_min'] = salary_min
                        vacancy_data['salary_max'] = salary_max
                    except:
                        vacancy_data['salary_min'] = None
                        vacancy_data['salary_max'] = None

                    vacancy_data['website'] = 'https://www.superjob.ru/'
                    vacancy_list_sj.append(vacancy_data)
                    try:
                        vacancy_db.insert_one(vacancy_data)
                    except errors.DuplicateKeyError:
                        continue
            else:
                break
    return vacancy_list_sj


pos = ['Бухгалтер']
p = 2
s = 30000
url_hh = 'https://hh.ru/'
url_sj = 'https://www.superjob.ru/'

hh = search_vacancy_hh(url_hh, pos, p, s)
sj = search_vacancy_sj(url_sj, pos, p, s)

vacancy_list = hh + sj

for uniq in vacancy_list:
    try:
        uniq.pop('_id')
    except:
        continue

# pprint(vacancy_list)

with open('hhsj_json.json', 'w') as f:
    json.dump(vacancy_list, f)

# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы
# (необходимо анализировать оба поля зарплаты).

for i in vacancy_db.find({'$or': [{'salary_max': 70000}, {'salary_min': 70000}]}):
    pprint(i)

# Task_1. Альтернативно можно заполнять ДБ из JSON-a

# with open('hhsj_json.json') as f:
#     v_list = json.load(f)
#
# for i in v_list:
#     vacancy_db.insert_one(i)


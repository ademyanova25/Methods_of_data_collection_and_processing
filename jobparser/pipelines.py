# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongobase = client['Library'].vacancy_spider

    def process_item(self, item, spider):
        my_item = dict(item)
        my_item['salary_min'], my_item['salary_max'] = self.process_salary(my_item['salary'], spider)
        my_item.pop('salary')
        if spider.name == 'hh':
            my_item['employer'] = ''
            for elem in my_item['employer_list']:
                my_item['employer'] += ''.join(elem)
        else:
            my_item['employer'] = ''.join(my_item['employer_list'])
        my_item['employer'].replace(u'\xa0', u'').replace(u'\u202f', u'')
        my_item.pop('employer_list')
        collection = self.mongobase[spider.name]
        collection.insert_one(my_item)
        return my_item

    def process_salary(self, salary, spider):
        try:
            if not salary:
                salary_min = None
                salary_max = None
            else:
                if spider.name == 'hh':
                    slr = salary.replace(u'\xa0', u'').replace(u'\u202f', u'').split('до')
                else:
                    sal = ''
                    for el in salary:
                        sal += ''.join(el)
                    slr = sal.replace(u'\xa0', u'').replace(u'\u202f', u'').split('—')
                slr[0] = re.sub(r'[^0-9]', '', slr[0])
                salary_min = int(slr[0])
                if len(slr) > 1:
                    slr[1] = re.sub(r'[^0-9]', '', slr[1])
                    salary_max = int(slr[1])
                else:
                    salary_max = salary_min
        except:
            salary_max = None
            salary_min = None
        return salary_min, salary_max

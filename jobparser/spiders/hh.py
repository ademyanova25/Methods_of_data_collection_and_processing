import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class HhSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?L_save_area=true&clusters=true&enable_snippets=true&text'
                  '=бухгалтер&area=1&experience=between3And6',
                  'https://hh.ru/search/vacancy?L_save_area=true&clusters=true&enable_snippets=true&text'
                  '=бухгалтер&area=1&experience=between1And3']

    def parse(self, response:HtmlResponse):
        vac_link = response.xpath('//a[@data-qa="vacancy-serp__vacancy-title"]/@href').getall()
        next_page = response.xpath('//a[@data-qa="pager-next"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for link in vac_link:
            yield response.follow(link, callback=self.vac_parse)

    def vac_parse(self, response:HtmlResponse):
        name = response.xpath('//h1/text()').get()
        salary = response.xpath('//p[@class="vacancy-salary"]/span/text()').get()
        link = response.url
        employer_list = response.xpath('//a[@class="vacancy-company-name"]/span/text() | //a['
                                       '@class="vacancy-company-name"]/span/span/text()').extract()
        item = JobparserItem(name=name, salary=salary, link=link, employer_list=employer_list)
        yield item


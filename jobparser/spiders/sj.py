import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjSpider(scrapy.Spider):
    name = 'sj'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vakansii/buhgalter.html?geo%5Bt%5D%5B0%5D=4']

    def parse(self, response: HtmlResponse):
        vac_link = response.xpath('//a[contains(@class, "_2JivQ _1UJAN")]/@href').getall()
        next_page = response.xpath('//a[@rel="next"][2]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for link in vac_link:
            yield response.follow(link, callback=self.vac_parse)

    def vac_parse(self, response: HtmlResponse):
        name = response.xpath('//h1/text()').get()
        salary = response.xpath('//span[@class="_1OuF_ ZON4b"]/span[1]/span/text() | //span[@class="_1OuF_ '
                                'ZON4b"]/span[1]/span/span/text()').getall()
        link = response.url
        employer_list = response.xpath('//div[contains(@class, "_3zucV _2cmJQ _1SCYW")]/a/h2/text() | //div[contains('
                                       '@class, "_1Tjoc kNkIq _1RZnn _3B6FR _1sXOS _3lvIR")]/div[2]/div/span/text('
                                       ')').getall()
        item = JobparserItem(name=name, salary=salary, link=link, employer_list=employer_list)
        yield item

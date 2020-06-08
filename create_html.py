import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_selenium import SeleniumRequest



class htmlSpider(scrapy.Spider):
    '''Simple scraper to copy a page's HTML, for local development'''

    name = "spider"

    def __init__(self, js=False, **kwargs):
        super().__init__(**kwargs)
        self.js = js

    def start_requests(self):
        urls = [
            'https://www.immowelt.de/expose/2vekd44']
        for url in urls:
            if self.js:
               yield SeleniumRequest(url=url, callback=self.parse)
            else:
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # write out the html
        html_file = "./html/immowelt-expose-2vekd44.html"
        with open(html_file, 'wb') as fout:
            fout.write(response.body)


process = CrawlerProcess()
process.crawl(htmlSpider,js=True)
process.start()

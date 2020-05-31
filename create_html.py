import scrapy
from scrapy.crawler import CrawlerProcess


class spider(scrapy.Spider):
    '''Simple scraper to copy a page's HTML, for local development'''

    name = "spider"

    def start_requests(self):
        urls = [
            'https://www.wg-gesucht.de/wohnungen-in-Berlin-Kreuzberg.4058192.html']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # write out the html
        html_file = "wohnungen-in-Berlin-Kreuzberg.4058192.html"
        with open(html_file, 'wb') as fout:
            fout.write(response.body)


process = CrawlerProcess()
process.crawl(spider)
process.start()

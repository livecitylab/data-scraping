import scrapy
from scrapy.crawler import CrawlerProcess


class proxiesSpider(scrapy.Spider):
    '''Gets a list of IPs and ports from https://free-proxy-list.net/ and writes it to a txt file,
      to be used by scrapy-rotating-proxies'''

    name = "proxiesSpider"

    def start_requests(self):
        url = 'https://free-proxy-list.net/'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # get all proxies and their ports
        proxy_table = response.css('table#proxylisttable')
        proxy_table_rows = proxy_table.xpath(
            './/tr')[1:]  # remove table header
        proxy_file = "proxies/proxies.txt"
        with open(proxy_file, 'w') as fout:
            for row in proxy_table_rows:
                ip = row.xpath('./td[1]/text()').extract_first()
                port = row.xpath('./td[2]/text()').extract_first()
                if ip and port:
                    print(ip)
                    print(port)
                    proxy = ':'.join([ip, port])
                    fout.write(proxy)
                    fout.write('\n')
        fout.close()


process = CrawlerProcess()
process.crawl(proxiesSpider)
process.start()

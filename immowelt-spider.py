# import pandas as pd
# import re
import scrapy
# import json
# from datetime import datetime
from scrapy.crawler import CrawlerProcess

class wgGesucht(scrapy.Spider):
    '''Crawls the first page of WG-Gesucht, then all they offers it find and get all rent data'''
    name = "dc_chapter_spider"

    def start_requests(self):
        # url = 'https://www.wg-gesucht.de/wohnungen-in-Berlin.8.2.1.1.html?category=2&city_id=8&rent_type=0&img=1&rent_types%5B0%5D=0'
        filename = 'immowelt-home-berlin-aktuellste'
        url = 'file:///Users/danroc/Documents/Projects/@techlabs/data-scraping/html/'+filename+'.html'
        yield scrapy.Request(url=url, callback=self.parse_home)

    def parse_home(self, response):
        iw_lists = response.css('div.iw_list_content')
        iw_items = [i.css('div.listitem_wrap') for i in iw_lists]
        print(len(iw_items))

        # offers = response.css('div.offer_list_item')
        # links = offers.xpath('//h3/a/@href').extract()
        # for url in links:
        #     if not url.startswith("http"):
        #         yield response.follow(url=url, callback=self.parse_pages)

# offers_list = []
process = CrawlerProcess()
process.crawl(wgGesucht)
process.start()
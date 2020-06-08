import pandas as pd
import re
import time
import scrapy
import json
import random
from datetime import datetime
from scrapy.crawler import CrawlerProcess


class immoscout(scrapy.Spider):
    '''Crawls the first page of WG-Gesucht, then all they offers it find and get all rent data'''
    name = "immoscout"

    def start_requests(self):
        url = 'https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-mieten'
        yield scrapy.Request(url=url, callback=self.parse_offer_list)

    def parse_offer_list(self, response):
        offers = response.css('ul#resultListItems > li')
        for offer in offers:
            url = offer.xpath('.//a[1]/@href').extract_first()
            if url:
                time.sleep(random.randint(1,5))
                yield response.follow(url=url, callback=self.write_html_files)

    def write_html_files(self, response):
        '''Used just for development, to write local html files and avoid hitting the server everytime'''
        id = response.url.split('/')[-1].replace('.html', '')
        html_file = "./html/immoscout/immoscout-expose-"+id+".html"
        with open(html_file, 'wb') as fout:
            fout.write(response.body)

    def parse_offer(self, response):
        '''Parse each offer page'''
        # append to final list
        #offers_list.append(offer)
        pass


offers_list = []
process = CrawlerProcess()
process.crawl(immoscout)
process.start()

for offer in offers_list:
    print(json.dumps(offer, indent=4))

# writing JSON object
# now = str(datetime.now())
# with open('./data/'+now+'_wg-gesucht.json', 'w') as f:
#     json.dump(offers_list, f)
#
# # writing excel and csv
# df = pd.DataFrame(offers_list)
# df.to_csv('./data/'+now+'_wg-gesucht.csv')
# df.to_excel('./data/'+now+'_wg-gesucht.xlsx')

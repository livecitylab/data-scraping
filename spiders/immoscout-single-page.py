import pandas as pd
from datetime import datetime
import json
import glob
import os
from locale import atof, setlocale, LC_NUMERIC
import re  # regex
import scrapy
from scrapy.crawler import CrawlerProcess

PATH = "file:///Users/danroc/Documents/Projects/@techlabs/data-scraping/html/immoscout/"
setlocale(LC_NUMERIC, 'de_DE')

class immoscout(scrapy.Spider):
    '''Local development mode: uses a downloaded HTML file to avoid hitting the servers every time'''

    name = "immoscout"

    def start_requests(self):
        # using local file, hardcoded
        # TODO: refactor to maybe get the html file from a given relative path
        os.chdir('/data-scraping/html/immoscout/')
        files = glob.glob('immoscout-expose-*.html')
        # url = PATH + files[4]
        # yield scrapy.Request(url=url, callback=self.parse)
        for file in files:
            url = PATH + file
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Code to parse course pages ## Fill in dc_dict here
        # parsing each entry
        offer = dict()

        # get main data from the html's head
        head = response.xpath('/html/head')
        offer['title'] = head.css('title::text').get()
        offer['image'] = head.xpath(
            './meta[@property="og:image"]/@content').get()
        offer['url'] = response.url
        offer['description'] = head.xpath(
            './meta[@name="description"]/@content').get()

        # ADDRESS
        address_block = response.xpath('//div[@class="address-block"]')[0]
        address = address_block.xpath('.//text()').getall()
        offer['address'] = '\n'.join([i.strip() for i in address if len(i.strip()) > 0])

        # PRICES
        # offer['kaltmiete'] = atof(response.css('div.is24qa-kaltmiete::text').get().strip().split(' ')[0])
        offer['num_rooms'] = atof(response.css('div.is24qa-zi::text').get().strip())
        offer['area'] = atof(response.css('div.is24qa-flaeche::text').get().strip().split(' ')[0])

        # MERKMALE
        offer['merkmale'] =  response.css('div.criteriagroup.boolean-listing > span.palm-hide::text').getall()

        details = response.css('dl.grid')
        for detail in details:
            key = detail.xpath('./dt/text()').get().strip()
            value = detail.xpath('./dd//text()').getall()
            value = [i.strip() for i in value if len(i.strip()) > 0]
            # TODO: need to convert values to floats
            if (len(value) == 1):
                value = value[0].strip()
            if key == 'Kaltmiete':
                value = value[0].split(' ')[0]
            if key == 'Nebenkosten':
                value = value[1].split(' ')[0]
            if key == 'Gesamtmiete':
                value = value.split(' ')[0]
            if 'Kaution' in key:
                value = value[0]
            if key == "Wohnfläche ca.":
                key = 'area'
                value = value.split(' ')[0]
            if key == "Zimmer":
                key = 'num_rooms'
                value = value
            offer[key.lower()] = value

        # LONG TEXT
        offer['object_description'] = response.css('pre.is24qa-objektbeschreibung::text').get()
        offer['ausstattung'] = response.css('pre.is24qa-ausstattung::text').get()
        offer['lage'] = response.css('pre.is24qa-lage::text').get()
        offer['sonstiges'] = response.css('pre.is24qa-sonstiges::text').get()

        # append to final list
        offers_list.append(offer)


offers_list = []
process = CrawlerProcess()
process.crawl(immoscout)
process.start()

for offer in offers_list:
    print(json.dumps(offer, indent=4))

os.chdir('/data-scraping/data/immoscout')

# writing JSON object
now = str(datetime.now())
with open(now+'_immoscout.json', 'w') as f:
    json.dump(offers_list, f)

# writing excel and csv
df = pd.DataFrame(offers_list)
df.to_csv(now+'_immoscout.csv')
df.to_excel(now+'_immoscout.xlsx')

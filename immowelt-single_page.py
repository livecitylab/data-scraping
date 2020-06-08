import pandas as pd
from datetime import datetime
import json
import glob
import os
from locale import atof, setlocale, LC_NUMERIC
import re  # regex
import scrapy
from scrapy.crawler import CrawlerProcess

PATH = "file:///Users/danroc/Documents/Projects/@techlabs/data-scraping/html/immowelt/"
setlocale(LC_NUMERIC, 'de_DE')

class immowelt(scrapy.Spider):
    '''Local development mode: uses a downloaded HTML file to avoid hitting the servers every time'''

    name = "immowelt"

    def start_requests(self):
        # url = 'https://www.wg-gesucht.de/wohnungen-in-Berlin-Friedrichshain.6401013.html'
        # using local file, hardcoded
        # TODO: refactor to maybe get the html file from a given relative path
        os.chdir('/Users/danroc/Documents/Projects/@techlabs/data-scraping/html/immowelt/')
        files = glob.glob('immowelt-expose*.html')
        url = PATH + files[2]
        yield scrapy.Request(url=url, callback=self.parse)
        # for file in files:
        #     url = PATH + file
        #     yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Code to parse course pages ## Fill in dc_dict here
        # parsing each entry
        offer = dict()

        # get main data from the html's head
        head = response.xpath('/html/head')
        offer['title'] = head.xpath(
            './meta[@property="og:title"]/@content').extract_first()
        offer['image'] = head.xpath(
            './meta[@property="og:image"]/@content').extract_first()
        offer['url'] = response.url
        offer['description'] = head.xpath(
            './meta[@name="description"]/@content').extract_first()

        quickfacts = response.css('div.quickfacts')
        offer['summary_text'] = quickfacts.css('h1::text').extract_first()
        offer['location'] = quickfacts.xpath('./div[@class="location"]/span[1]/text()').extract_first()
        offer['merkmale'] = quickfacts.css('div.merkmale::text').extract_first()

        hardfacts = response.css('div.hardfacts')
        offer['total_price'] = float(hardfacts.xpath('./div[1]/strong/text()').extract_first().split(' ')[0].replace('.',''))
        offer['area'] = atof(hardfacts.xpath('./div[2]/text()').extract_first().split(' ')[0].strip())
        offer['num_rooms'] = atof(hardfacts.xpath('./div[3]/text()').extract_first().strip())

        # PREISE UND KOSTEN
        preise_container = response.xpath('//h2[contains(text(), "Preise")]/..')

        ## KALTMIETE
        container = preise_container.xpath('.//strong[contains(text(), "Kaltmiete")]/../..')
        if len(container) > 0:
            offer['kaltmiete'] = atof(container.css('div.datacontent > strong::text').extract_first().split(' ')[0].strip())

        ## NEBENKOSTEN
        container = preise_container.xpath('.//div[contains(text(), "Nebenkosten")]/../..')
        if len(container) > 0:
            offer['nebenkosten'] = atof(container.css('div.datacontent::text').extract_first().split(' ')[0].strip())

        ## HEIZKOSTEN
        container = preise_container.xpath('.//div[contains(text(), "Heizkosten")]/../..')
        if len(container) > 0:
            offer['heizkosten'] = container.css('div.datacontent::text').extract_first()

        ## WARMMIETE
        container = preise_container.xpath('.//div[contains(text(), "Warmmiete")]/../..')
        if len(container) > 0:
            offer['warmmiete'] = container.css('div.datacontent::text').extract_first()

        ## KAUTION
        container = response.xpath('//div[contains(text(), "Kaution")]/..')
        if len(container) > 0:
            offer['kaution'] = atof(container.css('div.section_content > p::text').extract_first().strip().split(' ')[0])

        # Get the parent div of the div whose content is 'Immobilie' to get the online ID
        immobilie_container = response.xpath('//h2[contains(text(), "Immobilie")]/../..')
        offer['online_id'] = immobilie_container.css('div.section_content > p::text').extract_first().strip().replace('Online-ID: ', '')

        # Get the parent div of the div whose content is 'Die Wohnung' to get details
        # TODO: Needs some text recognition to get main facts?
        # whg_container = response.xpath('//div[contains(text(), "Die Wohnung")]/..')
        # offer['type'] = whg_container.xpath('./div[2]/p/text()').extract_first().strip()
        # offer['floor'] = whg_container.xpath('./div[2]/p/span/text()').extract_first().strip()
        # offer['availability'] = whg_container.xpath('./div[2]/p/strong/text()').extract_first().strip()
        # TODO: get more details from UL > LIs?

        # Get the parent div of the div whose content is 'Wohnalage' to get details
        whg_container = response.xpath('//div[contains(text(), "Wohnanlage")]/..')
        offer['building_year'] = whg_container.xpath('./div[2]/p/text()').extract_first().strip()
        # TODO: get more details from UL > LIs?

        # Get the parent div of the div whose content is 'Objektbeschreibung' to get details
        container = response.xpath('//div[contains(text(), "Objektbeschreibung")]/..')
        text_content = container.xpath('./div[2]/p//text()').extract()
        offer['object_description'] = '\n'.join([i.strip() for i in text_content if len(i.strip()) > 0])

        # Get the parent div of the div whose content is 'Ausstattung' to get details
        container = response.xpath('//div[contains(text(), "Ausstattung")]/..')
        text_content = container.xpath('./div[2]/p//text()').extract()
        offer['ausstattung'] = '\n'.join([i.strip() for i in text_content if len(i.strip()) > 0])

        # Get the parent div of the div whose content is 'Sonstiges' to get details
        container = response.xpath('//div[contains(text(), "Sonstiges")]/..')
        if len(container) > 0:
            text_content = container.xpath('./div[2]/p//text()').extract()
            offer['sonstiges'] = '\n'.join([i.strip() for i in text_content if len(i.strip()) > 0])

        # Get the parent div of the div whose content is 'KFZ Stellplatz' to get details
        container = response.xpath('//div[contains(text(), "KFZ Stellplatz")]/..')
        text_content = container.xpath('./div[2]/p//text()').extract()
        offer['kfz_stellplatz'] = '\n'.join([i.strip() for i in text_content if len(i.strip()) > 0])

        # Get the parent div of the div whose content is 'Stichworte' to get details
        container = response.xpath('//div[contains(text(), "Stichworte")]/..')
        text_content = container.xpath('./div[2]/p//text()').extract()
        offer['keywords'] = '\n'.join([i.strip() for i in text_content if len(i.strip()) > 0])

        # Get the parent div of the div whose content is 'Lagebeschreibung' to get details
        container = response.xpath('//div[contains(text(), "Lagebeschreibung")]/..')
        text_content = container.xpath('./div[2]/p//text()').extract()
        offer['lagebeschreibung'] = '\n'.join([i.strip() for i in text_content if len(i.strip()) > 0])

        # append to final list
        offers_list.append(offer)


offers_list = []
process = CrawlerProcess()
process.crawl(immowelt)
process.start()

for offer in offers_list:
    print(json.dumps(offer, indent=4))

os.chdir('/Users/danroc/Documents/Projects/@techlabs/data-scraping/data/immowelt')

# writing JSON object
now = str(datetime.now())
with open(now+'_immowelt.json', 'w') as f:
    json.dump(offers_list, f)

# writing excel and csv
df = pd.DataFrame(offers_list)
df.to_csv(now+'_immowelt.csv')
df.to_excel(now+'_immowelt.xlsx')

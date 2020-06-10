import json
import re  # regex
import scrapy
from scrapy.crawler import CrawlerProcess


class wgGesucht(scrapy.Spider):
    '''Local development mode: uses a downloaded HTML file to avoid hitting the servers every time'''

    name = "wgGesucht"

    def start_requests(self):
        # url = 'https://www.wg-gesucht.de/wohnungen-in-Berlin-Friedrichshain.6401013.html'
        # using local file, hardcoded
        # TODO: refactor to maybe get the html file from a given relative path
        url = 'file:///Users/danroc/Documents/Projects/@techlabs/data-scraping/html/wohnungen-in-Berlin-Steglitz.7453024.html'
        yield scrapy.Request(url=url, callback=self.parse)

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
        offer['url'] = head.xpath(
            './meta[@property="og:url"]/@content').extract_first()

        key_facts = response.css(
            'h2.headline-key-facts::text').extract()
        offer['area'] = float(re.findall(r'\d+', key_facts[0])[0])
        offer['total_price'] = float(re.findall(r'\d+', key_facts[1])[0])
        offer['num_rooms'] = float(re.findall(r'\d+', key_facts[2])[0])

        # cost breakdown table
        costs_div = response.xpath('//h3[contains(text(), "Kosten")]/..')
        costs_rows = costs_div.xpath('./table/tr')
        # offer['costs'] = dict()
        for row in costs_rows:
            # TODO: keys are in German, do we want to translate to English?
            key = row.xpath('./td[1]/text()').extract_first().strip().replace(':', '')
            if len(key) > 0:
                value = row.xpath('./td[2]/b/text()').extract_first()
                if value != 'n.a.':
                    value = float(re.findall(
                        r'\d+', value)[0])
                # offer['costs'][key] = value
                offer[key] = value

        # address
        address_div = response.xpath('//h3[contains(text(), "Adresse")]/..')
        address_parts_dirty = address_div.xpath('./a/text()').extract()
        address_parts = [i.strip()
                         for i in address_parts_dirty if len(i.strip()) > 0]
        for i in range(len(address_parts)):
            address_parts[i] = address_parts[i].strip()
        offer['address'] = ', '.join(address_parts)

        # availability
        availability_div = response.xpath(
            '//h3[contains(text(), "Verfügbarkeit")]/..')
        availability_parts_dirty = availability_div.xpath(
            './p//text()').extract()
        availability = [i.strip() for i in availability_parts_dirty if len(i.strip()) > 0]
        offer['from_date'] = availability[1]
        # check if there is a "frei bis" date
        if len(availability) == 4:
            offer['to_date'] = availability[3]

        # time the offer has been online
        # can be either "X Stunden" or a date
        # TODO: always get a date and time (calculate when it is "X Stunden")
        offer['online_since'] = response.xpath(
            '//b[contains(text(), "Online")]/text()').extract_first().strip().replace('Online: ', '')

        # List of facts about the offer ("Altbau", "3. OG", "mobliert", "Eigene Kuche", etc)
        # TODO: figure out all the possibilities and put them into their own columns, with a True or False value
        facts_div = response.xpath(
            '//h3[contains(text(), "Angaben zum Objekt")]/..')
        facts_dirty = facts_div.css('div.row ::text').extract()
        for i in range(len(facts_dirty)):
            facts_dirty[i] = ' '.join(facts_dirty[i].split())
        offer['facts'] = [i.strip()
                          for i in facts_dirty if len(i.strip()) > 0]

        # free text description of the ads
        # there are 3 types of blocks, each with an id of freitext_X
        # freitext_0 = "Wohnung"
        # freitext_1 = "Lage"
        # freitext_2 = ? , not existing
        # freitext_3 = "Sonstiges"
        description_divs = response.xpath(
            '//div[contains(@id, "freitext")]')
        keys = ["Wohnung", "Lage", "X", "Sonstiges"] # TODO: figure out if X is something
        for div in description_divs:
            text_list = div.xpath('./p[1]//text()').extract()
            if len(text_list) > 0:
                # get the title based on the last number of the div id ("freitext_01", for ex)
                div_id = div.xpath('./@id').extract_first()
                title = keys[int(div_id[-1])]
                offer[title] = ' '.join(text_list).strip()
        # append to final list
        offers_list.append(offer)


offers_list = []
process = CrawlerProcess()
process.crawl(wgGesucht)
process.start()

for offer in offers_list:
    print(json.dumps(offer, indent=4))

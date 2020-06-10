import pandas as pd
import re
import scrapy
import json
from datetime import datetime
from scrapy.crawler import CrawlerProcess

class wgGesucht(scrapy.Spider):
    '''Crawls the first page of WG-Gesucht, then all they offers it find and get all rent data'''
    name = "wg-gesucht"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next_page = 0
        self.num_pages_to_crawl = 3
        self.pagination_links = []

    def start_requests(self):
        url = 'https://www.wg-gesucht.de/wohnungen-in-Berlin.8.2.1.0.html'
        yield scrapy.Request(url=url, callback=self.parse_offer_list)

    def parse_offer_list(self, response):
        #get page links when run for the first time
        if len(self.pagination_links) == 0:
            self.pagination_links = response.css('ul.pagination > li > a.a-pagination::attr(href)').getall()
        # get current page
        current_page = response.css('ul.pagination > li.active > span::text').get().strip()
        # if already at the maximum number of pages that we want to crawl, end
        try:
            current_page = int(current_page)
        except:
            return
        if (current_page > self.num_pages_to_crawl ):
            return
        # otherwise, crawl offers in current page
        if (current_page == self.next_page +1):
            offers = response.css('div.offer_list_item')
            links = offers.xpath('//h3/a/@href').getall()
            for url in links:
                if not url.startswith("http"):
                    yield response.follow(url=url, callback=self.parse_offer)

            ## GO TO NEXT PAGE AND REPEAT
            next_page_url = self.pagination_links[self.next_page]
            self.next_page = self.next_page + 1
            if next_page_url:
                yield response.follow(url=next_page_url, callback=self.parse_offer_list)

    def parse_offer(self, response):
        # parsing each entry
        # TODO: use Srapy Item and Item Pipline instead of dict()
        # TODO: https://docs.scrapy.org/en/latest/topics/items.html
        offer = dict()

        # get main data from the html's head
        head = response.xpath('/html/head')
        offer['title'] = head.xpath(
            './meta[@property="og:title"]/@content').get()
        offer['image'] = head.xpath(
            './meta[@property="og:image"]/@content').get()
        offer['url'] = head.xpath(
            './meta[@property="og:url"]/@content').get()

        key_facts = response.css(
            'h2.headline-key-facts::text').getall()
        offer['area'] = float(re.findall(r'\d+', key_facts[0])[0])
        offer['total_price'] = float(re.findall(r'\d+', key_facts[1])[0])
        offer['num_rooms'] = float(re.findall(r'\d+', key_facts[2])[0])

        # cost breakdown table
        costs_div = response.xpath('//h3[contains(text(), "Kosten")]/..')
        costs_rows = costs_div.xpath('./table/tr')
        # offer['costs'] = dict()
        for row in costs_rows:
            # TODO: keys are in German, do we want to translate to English?
            key = row.xpath('./td[1]/text()').get().strip().replace(':', '')
            if len(key) > 0:
                value = row.xpath('./td[2]/b/text()').get()
                if value != 'n.a.':
                    value = float(re.findall(
                        r'\d+', value)[0])
                # offer['costs'][key] = value
                offer[key] = value

        # address
        address_div = response.xpath('//h3[contains(text(), "Adresse")]/..')
        address_parts_dirty = address_div.xpath('./a/text()').getall()
        address_parts = [i.strip()
                         for i in address_parts_dirty if len(i.strip()) > 0]
        for i in range(len(address_parts)):
            address_parts[i] = address_parts[i].strip()
        offer['address'] = ', '.join(address_parts)

        # availability
        availability_div = response.xpath(
            '//h3[contains(text(), "Verfügbarkeit")]/..')
        availability_parts_dirty = availability_div.xpath(
            './p//text()').getall()
        availability = [i.strip() for i in availability_parts_dirty if len(i.strip()) > 0]
        offer['from_date'] = availability[1]
        # check if there is a "frei bis" date
        if len(availability) == 4:
            offer['to_date'] = availability[3]

        # time the offer has been online
        # can be either "X Stunden" or a date
        # TODO: always get a date and time (calculate when it is "X Stunden")
        offer['online_since'] = response.xpath(
            '//b[contains(text(), "Online")]/text()').get().strip().replace('Online: ', '')

        # List of facts about the offer ("Altbau", "3. OG", "mobliert", "Eigene Kuche", etc)
        # TODO: figure out all the possibilities and put them into their own columns, with a True or False value
        facts_div = response.xpath(
            '//h3[contains(text(), "Angaben zum Objekt")]/..')
        facts_dirty = facts_div.css('div.row ::text').getall()
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
        keys = ["Wohnung", "Lage", "X", "Sonstiges"]  # TODO: figure out if X is something
        for div in description_divs:
            text_list = div.xpath('./p[1]//text()').getall()
            if len(text_list) > 0:
                # get the title based on the last number of the div id ("freitext_01", for ex)
                div_id = div.xpath('./@id').get()
                title = keys[int(div_id[-1])]
                offer[title] = ' '.join(text_list).strip()
        # append to final list
        offers_list.append(offer)


offers_list = []
process = CrawlerProcess()
process.crawl(wgGesucht)
process.start()

# for offer in offers_list:
#     print(json.dumps(offer, indent=4))

# writing JSON object
now = str(datetime.now())
with open('../data/wg-gesucht/'+now+'_wg-gesucht.json', 'w') as f:
    json.dump(offers_list, f)

# writing excel and csv
df = pd.DataFrame(offers_list)
df.to_csv('../data/wg-gesucht/'+now+'_wg-gesucht.csv')
df.to_excel('../data/wg-gesucht/'+now+'_wg-gesucht.xlsx')

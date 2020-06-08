# from scrapy_selenium import SeleniumRequest
import time

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import scrapy
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.crawler import CrawlerProcess

class immoweltApiSpider(scrapy.Spider):
    name = 'immoweltSpider'

    def __init__(self, js=False, **kwargs):
        super().__init__(**kwargs)
        self.js = js
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

    @staticmethod
    def get_selenium_response(driver, url, num_ids):
        '''Because Immowelt uses lazy-loading as you scroll to show all offers,
        this method first scrolls to the bottom of the page, then waits 5 seconds and checks if all offer ids are loaded,
        before passing the response back to scrapy'''

        driver.get(url)
        try:
            def scroll_down(driver):
                """A method for scrolling the page."""
                # Get scroll height.
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    # Scroll down to the bottom.
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    # Wait to load the page.
                    time.sleep(2)
                    # Calculate new scroll height and compare with last scroll height.
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height

            def find(driver):
                '''Check if all offers are loaded'''
                iw_items = driver.find_elements_by_class_name('listitem_wrap')
                if len(iw_items) == num_ids:
                    return iw_items
                else:
                    return False

            # first, scroll down
            scroll_down(driver)
            # then wait 5 seconds and check for the offers
            element = WebDriverWait(driver, 5).until(find)
            # if all ok, return response
            return driver.page_source.encode('utf-8')
        except:
            driver.quit()

    def start_requests(self):
        urls = ['https://www.immowelt.de/liste/berlin/wohnungen/mieten?sort=createdate%2Bdesc']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # in the Immowelt page there is a hidden input field with the values of all ids to be displayed in the page
        # we use these values to determine how many offers should be displayed on the page, after all lazy-loading is done.
        estateIds = response.xpath('//input[@id="estateIds"]/@value').extract_first().split(',')
        num_estateIds = len(estateIds)
        # then we load the page with selenium
        first_response = response
        response = scrapy.Selector(
            text=self.get_selenium_response(self.driver, response.url, num_estateIds))

        # get all offer divs
        offer_divs = response.css('div.listitem_wrap')
        for offer_div in offer_divs:
            estateId = offer_div.xpath('./@data-estateid').extract_first()
            url = offer_div.css('div.listitem > a::attr(href)').extract_first()
            yield first_response.follow(url=url, callback=self.parse_offer, meta={'estateId':estateId})

    def parse_offer(self, response):
        # write out the html
        html_file = "./html/immowelt-expose"+ response.meta.get('estateId') +".html"
        with open(html_file, 'wb') as fout:
            fout.write(response.body)




process = CrawlerProcess()
process.crawl(immoweltApiSpider, js = True)
process.start()
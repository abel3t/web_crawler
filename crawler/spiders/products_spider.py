import scrapy
import os
import time
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
basedir = os.path.dirname(os.path.realpath('__file__'))


class ProductsSpider(scrapy.Spider):
    name = 'products'
    start_urls = ['https://www.bestieship.com/collections/buttrfly-canvas']
    page_no = 2
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_argument("--incognito")
    options.add_argument("--disable-extensions")
    options.add_argument(" --disable-gpu")
    options.add_argument(" --disable-infobars")
    handle_httpstatus_list = [403, 504]

    def parse(self, response):

        chrome_driver_path = os.path.join(basedir, 'chromedriver')
        driver = webdriver.Chrome(chrome_options=self.options, executable_path='/Users/tamto/Documents/chromedriver')
        driver.get('https://www.bestieship.com/collections/buttrfly-canvas')

        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000);")
            time.sleep(0.5)
            new_height = driver.execute_script("return document.body.scrollHeight - 1000")
            if new_height == last_height:
                break
            last_height = new_height
            time.sleep(0.5)

        scrapy_selector = Selector(text=driver.page_source)
        products = scrapy_selector.css("div.thumbnail")
        for product in products:
            print(product, 'product')
            yield {
                'title': product.css('span.title::text').get(),
                'image_url': product.css('div.image__container img::attr(src)').get()[2:]
            }

        driver.close()

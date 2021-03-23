import scrapy
import os

basedir = os.path.dirname(os.path.realpath('__file__'))


class OhhgearsSpider(scrapy.Spider):
    name = 'ohhgears'
    base_url = 'https://ohhgears.com/?page=%s'
    start_urls = [base_url % 1]
    download_delay = 5

    def parse(self, response):
        self.log('Visited ' + response.url)

        products = response.css('.container .row .col-md-3')
        for product in products:
            item_link = 'https://ohhgears.com' + product.css('.col-md-3 a.site-heading-link::attr(href)').get()
            item = {
                'title': product.css('h4.site-heading.campaign-heading.campaign-heading-ellipsed::text').get(),
                'image_url': product.css('.site-heading-link img::attr(src)').get()[2:],
                'slash_price': product.css('.col-md-3 > .site-heading .slash-price::text')
                    .get().replace('\t', '').replace('\n', ''),
                'price': product.css('.col-md-3 > h4.site-heading.campaign-heading::text')
                    .extract()[1].replace('\t', '').replace('\n', '')
            }

            self.log(item_link)

            yield scrapy.Request(url=item_link, meta={'item': item}, callback=self.get_detail)

        next_page_url = response.css('div.row.searchPagination > div > nav > ul > li:nth-child(2) a::attr(href)').extract_first()
        next_page_url = response.urljoin(next_page_url)
        yield scrapy.Request(url=next_page_url, callback=self.parse)

    def get_detail(self, response):
        self.log('Visited' + response.url)
        item = response.meta['item']
        images = response.css('.thumb-outter .thumb-box')
        image_urls = []
        for image in images:
            image_urls.append(image.css('.thumb-inner img::attr(src)').get()[2:])
        item['image_urls'] = image_urls
        return item

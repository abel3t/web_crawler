import scrapy
import os
import re
from datetime import date

basedir = os.path.dirname(os.path.realpath('__file__'))


class CellPhonesMobileSpider(scrapy.Spider):
    name = 'cellphones_mobile'
    base_url = 'https://cellphones.com.vn/mobile.html?p=%s'
    start_urls = [base_url % 1]
    download_delay = 5

    def parse(self, response):
        self.log('Visited ' + response.url)

        products = response.css('.products-container .cols-5 .cate-pro-short')

        self.log('products ' + str(len(products)))
        for product in products:
            title = name_processing(product.css('a > #product_link::text').get())
            item_link = product.css('li.cate-pro-short > div.lt-product-group-image > a::attr(href)').get()
            item = {
                'ten': title,
                'url': item_link,
                #
                'image': product.css('li.cate-pro-short > div.lt-product-group-image > a > img::attr(data-src)').get(),
                'ngay': date.today().strftime("%d/%m/%Y"),
                'loaisanpham': 'dienthoai'
            }
            self.log(item_link)

            yield scrapy.Request(url=item_link, meta={'item': item}, callback=self.get_detail)
            yield item


        next_page_url = response.css('div.row.searchPagination > div > nav > ul > li:nth-child(2) a::attr(href)').extract_first()
        next_page_url = response.urljoin(next_page_url)
        yield scrapy.Request(url=next_page_url, callback=self.parse)

    def get_detail(self, response):
        self.log('Visited ' + response.url)
        item = response.meta['item']
        attributes = []
        _attributes = response.css('ul#configurable_swatch_color')
        for attribute in _attributes:
            option_name = attribute.css('li > a > label > span.opt-name::text').get()
            option_price = attribute.css('li > a > label > span.opt-price::text').get()
            attributes.append({
                'option_name': option_name,
                'option_price': option_price
            })

        item['thuoctinh'] = attributes

        return item

def name_processing(name_pd):
    pattern = r'([^Chính hãng,chính hãng,VN/A,Điện thoại,điện thoại,|])\w+'
    print(name_pd)

    matches = re.finditer(pattern, name_pd)
    name_pd = [x.group() for x in matches]
    name_pd = list(map(lambda p: '\t'.join(p.split('/')), name_pd))

    return ' '.join(name_pd)
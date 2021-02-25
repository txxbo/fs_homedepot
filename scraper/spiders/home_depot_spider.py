import json
import scrapy
from scraper import db
from scraper.models import Product, User
from datetime import datetime
from scraper.items import HomeDepotItem


class HomeDepotSpider(scrapy.Spider):
    name = "home_depot_spider"
    allowed_domains = ["homedepot.com"]

    def __init__(self, url=None, **kwargs):
        self.url = url
        super().__init__(**kwargs)

    def start_requests(self):
        if self.url is not None:
            print(self.url)
            urls = [self.url]
        else:
            products = Product.query.filter_by(enabled=True).all()
            urls = [product.url for product in products]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        item = HomeDepotItem()
        data = self.get_json(response)

        item['url'] = response.request.url
        item['title'] = data.get('name', '')
        item['product_id'] = data.get('productID', '')
        item['checked_date'] = datetime.utcnow()
        item['availability'] = False
        item['price'] = 0.0

        offers = data.get('offers', None)
        if offers is not None:
            if offers.get('availability', None) is not None:
                item['availability'] = True

            item['price'] = offers.get('price', 0)

        yield item

    @staticmethod
    def get_json(response):
        scripts = response.xpath(
            '//script[@type="application/ld+json"]//text()')

        for ld_json in scripts:
            data = json.loads(ld_json.extract())
            if data['@type'] == 'Product':
                return data
        return {}

import json
import scrapy
from datetime import datetime
from scraper.items import HomeDepotItem


class HomeDepotSpider(scrapy.Spider):
    name = "home_depot_spider"
    allowed_domains = ["homedepot.com"]

    def start_requests(self):
        urls = [
            "https://www.homedepot.com/p/Milwaukee-M12-FUEL-12-Volt-Lithium-Ion-Brushless-Cordless-1-4-in-Hex-Impact-Driver-Kit-with-Free-M12-Rotary-Tool-2553-22-2460-20/315477815",
            "https://www.homedepot.com/p/Milwaukee-M18-FUEL-SURGE-18-Volt-Lithium-Ion-Brushless-Cordless-1-4-in-Hex-Impact-Driver-Tool-Only-2760-20/300193508"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        item = HomeDepotItem()
        data = self.get_json(response)

        item['title'] = data.get('name', '')
        item['product_id'] = data.get('productID', '')
        item['checked_date'] = datetime.utcnow()
        item['availability'] = False
        item['price'] = 0

        offers = data.get('offers', None)
        if offers is not None:
            if offers.get('availability', None) is not None:
                item['availability'] = True

            item['price'] = offers.get('price', 0)

        item['notify'] = item['availability']
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

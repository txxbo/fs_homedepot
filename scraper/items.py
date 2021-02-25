# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class HomeDepotItem(Item):
    product_id = Field()
    url = Field()
    title = Field()
    checked_date = Field()
    availability = Field()
    price = Field()


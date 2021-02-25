# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scraper import db
from scraper.models import Product, User


class ScraperPipeline:
    def __init__(self):
        self.available_items = []

    def close_spider(self, spider):
        # updates available to users logged in
        users = User.query.all()
        for user in users:
            user.updates_available = True

        if len(self.available_items) > 0:
            print("Sending email about the following items: ")
            print([product.product_id for product in self.available_items])
            # send an email with newly available items
            #   only 5 recipients allowed with free account

        db.session.commit()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        url = adapter.get('url')
        product = Product.query.filter_by(url=url).first()

        if product is None:
            # print(f"Product not found, adding to database!")
            product = Product()
            product.product_id = adapter.get('product_id')
            product.title = adapter.get('title')
            product.created = adapter.get('checked_date')
            product.last_check = adapter.get('checked_date')
            product.url = adapter.get('url')
            product.price = adapter.get('price')
            product.enabled = True
            product.availability = adapter.get('availability')
            if product.availability is True:
                self.available_items.append(product)
            db.session.add(product)
        else:
            # print(f"Product found, updating database!")
            product.title = adapter.get('title')
            product.product_id = adapter.get('product_id')
            product.last_check = adapter.get('checked_date')
            previously_available = product.availability
            product.availability = adapter.get('availability')
            product.price = adapter.get('price')
            if previously_available is False and product.availability is True:
                self.available_items.append(product)

        db.session.commit()
        return item

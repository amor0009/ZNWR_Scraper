import scrapy
from scrapy.crawler import CrawlerProcess


class ZNWRScraper(scrapy.Spider):
    name = "ZNWR"
    start_urls = ["https://znwr.ru/"]


    def parse(self, response):
        # Исключил "Sales week" у мужчин и женщин, иначе товары будут дублироваться в общем списке
        man_categories = (response.xpath("//div[@class='header__category-item'][2]"
                                        "//li[not(contains(@class, 'is-sales'))]//a/@href")
                          .getall())

        woman_categories = (response.xpath("//div[@class='header__category-item'][1]"
                                            "//li[not(contains(@class, 'is-sales'))]//a/@href")
                                            .getall())

        for category in man_categories:
            yield response.follow(category, self.parse_category, meta={"category": "man"})

        for category in woman_categories:
            yield response.follow(category, self.parse_category, meta={"category": "woman"})


    def parse_category(self, response):
        category = response.meta["category"]
        type = response.xpath("//span[@class='catalog__h1-span']/text()").get()
        product_links = response.xpath('//div[@class="card__product-name"]/a/@href').getall()
        for link in product_links:
            yield response.follow(link, self.parse_product, meta={"category": category, "type": type})


    def parse_product(self, response):
        category = response.meta["category"]
        type = response.meta["type"]
        product_name = response.xpath("//h1[@class='product__title']/text()").get()
        product_price = response.xpath("//div[@class='product__price-new']/text()").get()
        product_description = ''.join(response.xpath('(//div[contains(@class, "product__tabs-item")])[1]//div[contains(@class, "product__item-tabs-content")]//p/text()').getall()).strip()

        product_data = {
            "product_name": product_name.strip() if product_name else None,
            "product_price": product_price.strip() if product_price else None,
            "product_type": type.strip() if type else None,
            "product_description": product_description.strip() if product_description else None,
            "category": category,
            "product_link": response.url
        }

        yield product_data


process = CrawlerProcess(settings={
    "FEEDS": {
        "ZNWR_products.json": {"format": "json", "encoding": "utf8", "overwrite": True},
    },
    "LOG_LEVEL": "INFO",
})
process.crawl(ZNWRScraper)
process.start()

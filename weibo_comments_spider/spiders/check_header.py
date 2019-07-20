import scrapy
from scrapy import Request

class CheckHeader(scrapy.Spider):
    name = "check_header_spider"
    start_urls = ["https://httpbin.org/get?show_env=1"]

    def start_requests(self):
        for _ in range(10):
            yield Request("https://httpbin.org/get?show_env=1",
                          callback=self.parse,
                          dont_filter=True)

    def parse(self, response):
        print(response.text)

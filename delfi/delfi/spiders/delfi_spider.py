from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request
from urlparse import urljoin

from delfi.items import DelfiItem

class DelfiSpider(BaseSpider):
    name = "delfi"
    allowed_domains = ["delfi.lt"]
    start_urls = [
        "http://www.delfi.lt/archive/index.php?tod=29.11.2013&fromd=01.02.1999&channel=0&category=0&query=",
    ]

    def parse(self, response):
        sel = Selector(response)
        lis = sel.xpath('//div[@class="arch-search-list"]//div[@class="search-item-head"]/ancestor::li')
        for li in lis:
            item = DelfiItem()
            item['title'] = li.xpath("div/a[@class='arArticleT']/text()").extract()
            item['link'] = li.xpath("div/a[@class='arArticleT']/@href").extract()
            item['category'] = li.xpath("div/a[@class='section']/text()").extract()
            item['date'] = li.xpath("div/span/text()").extract()
            item['comments'] = li.xpath("div/a[@class='commentCount']/text()").extract()
            yield item

        for nextpage in sel.xpath('//a[@class="item next"]/@href').extract():
            nextpage = nextpage.replace("\t", "").replace("\n", '')
            yield Request(urljoin('http://www.delfi.lt', nextpage), callback=self.parse)

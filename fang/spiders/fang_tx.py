# -*- coding: utf-8 -*-
import scrapy


class FangTxSpider(scrapy.Spider):
    name = 'fang_tx'
    allowed_domains = ['fang.com']
    start_urls = ['http://www.fang.com/SoufunFamily.htm']

    def parse(self, response):
        pass

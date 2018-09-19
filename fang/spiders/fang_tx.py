# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request


class FangTxSpider(scrapy.Spider):
    name = 'fang_tx'
    allowed_domains = ['fang.com']
    start_urls = ['http://www.fang.com/SoufunFamily.htm']

    def parse(self, response):
        trs = response.xpath('//div[@class="outCont"]//tr')
        for tr in trs:
            tds = tr.xpath('.//td[not(@class)]')
            province_text = tds[0].xpath('.//text()').get()
            cities = tds[1].xpath('.//a')
            province_text = re.sub(r'\s', '', province_text)
            province = province_text if province_text else province
            if province == '其它':
                continue
            is_municipality = True if province == "直辖市" else False
            for city in cities:
                city_name = city.xpath('.//text()').get()
                city_link = city.xpath('.//@href').get()
                base_new_link = "http://newhouse.fang.com/house/s/"
                base_esf_link = "http://esf.fang.com/"
                base_zu_link = "http://zu.fang.com/"
                if city_name == "北京":
                    new_link = base_new_link
                    esf_link = base_esf_link
                    zu_link = base_zu_link
                else:
                    new_link = self._get_link(city_link, base_new_link)
                    esf_link = self._get_link(city_link, base_esf_link)
                    zu_link = self._get_link(city_link, base_zu_link)
                province = city_name if is_municipality else province
                yield Request(url=new_link, callback=self.parse_new_fang, meta={'city': (province, city_name)})
                yield Request(url=esf_link, callback=self.parse_esf_fang, meta={'city': (province, city_name)})
                yield Request(url=zu_link, callback=self.parse_zu_fang, meta={'city': (province, city_name)})

    def parse_new_fang(self, response):
        pass

    def parse_esf_fang(self, response):
        pass

    def parse_zu_fang(self, response):
        pass

    def _get_link(self, city_link, base_link):
        return city_link.split('.')[0] + '.' + base_link.split('//')[1]

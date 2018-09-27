# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request

from fang.items import NewHouseItem


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
        province, city = response.meta.get('city')
        lis = response.xpath('//div[contains(@class, "nl_con")]/ul/li')
        for li in lis:
            name = li.xpath(".//div[@class='nlcd_name']/a/text()").get().strip()
            house_type_list = li.xpath(".//div[contains(@class,'house_type')]/a/text()").getall()
            house_type_list = list(map(lambda x: re.sub(r'\s', '', x), house_type_list))
            rooms = list(filter(lambda x: x.endswith('居'), house_type_list))
            area = ''.join(li.xpath(".//div[contains(@class,'house_type')]/text()").getall()).strip()
            area = re.sub(r'\s|－|/|平米', '', area)
            address = li.xpath(".//div[@class='address']/a/@title").get()
            district_text = ''.join(li.xpath(".//div[@class='address']/a//text()").getall())
            district = re.search(r'.*?\[(.*)\].*', district_text).group(1)
            sale = li.xpath(".//div[contains(@class, 'fangyuan')]/span/text()").get()
            price = ''.join(li.xpath(".//div[@class='nhouse_price']//text()").getall())
            price = re.sub(r'\s|广告', '', price)
            url = li.xpath(".//div[@class='nlcd_name']/a/@href").get()
            item = NewHouseItem(province=province, city=city, name=name, rooms=rooms, area=area, address=address,
                                district=district, sale=sale, price=price, url=url)
            yield item
        next_url = response.xpath("//div[@class='page']//a[@class='next']/@href").get()
        if next_url:
            yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_new_fang, meta={'city': (province, city)})

    def parse_esf_fang(self, response):
        pass

    def parse_zu_fang(self, response):
        pass

    def _get_link(self, city_link, base_link):
        return city_link.split('.')[0] + '.' + base_link.split('//')[1]

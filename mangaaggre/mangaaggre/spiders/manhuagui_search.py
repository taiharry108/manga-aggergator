# -*- coding: utf-8 -*-
import scrapy
from ..manga_enum import MangaIndexTypeEnum
from ..items import MangaSearchResultItem
from urllib import parse
import json

class ManhuaduiSearchSpider(scrapy.Spider):
    name = 'manhuagui_search'
    allowed_domains = ['www.manhuagui.com']

    def start_requests(self):
        url = f'https://www.manhuagui.com/tools/word.ashx?key={parse.quote(getattr(self, "keyword", "test"))}'
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        result = json.loads(response.body_as_unicode())
        for d in result:
            name = d['t']
            url = d['u']
            if not url.startswith('http'):
                url = 'https://www.manhuagui.com/' + url.lstrip('/')
            yield MangaSearchResultItem(name=name, url=url)

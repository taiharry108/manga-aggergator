# -*- coding: utf-8 -*-
import scrapy
from ..manga_enum import MangaIndexTypeEnum
from ..items import MangaSearchResultItem
from urllib import parse
from scrapy.shell import inspect_response


class ManhuaduiSearchSpider(scrapy.Spider):
    name = 'manhuadui_search'
    allowed_domains = ['www.manhuadui.com']

    def start_requests(self):
        url = 'https://www.manhuadui.com/search/?keywords=' + \
            parse.quote(getattr(self, "keyword", "test"))
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        li_list = response.css('#w0 li.list-comic')
        for li in li_list:
            a = li.css('a.image-link')
            url = a.css('::attr(href)').get().lstrip('/')

            if not url.startswith('http'):
                url += 'https://www.manhuadui.com/'

            yield MangaSearchResultItem(name=a.css('::attr(title)').get(), url=url)

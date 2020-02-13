# -*- coding: utf-8 -*-
import scrapy
from ..manga_enum import MangaIndexTypeEnum
from ..items import MangaIndexItem


class ManhuaduiIndexSpider(scrapy.Spider):
    name = 'manhuadui_index'
    allowed_domains = ['www.manhuadui.com']

    def start_requests(self):
        url = 'https://www.manhuadui.com/manhua/' + getattr(self, 'keyword', 'test')
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        li_list = response.css('#chapter-list-1 li')
        name = response.css('.comic_deCon h1::text').get()
        for li in li_list:
            url = li.css('a::attr(href)').get().lstrip('/')
            if not url.startswith('http'):
                url = 'https://www.manhuadui.com/' + url
            title = li.css('a::attr(title)').get()
            type_ = MangaIndexTypeEnum.CHAPTER.value
            yield MangaIndexItem(name=name, title=title, type_=type_, url=url)

            

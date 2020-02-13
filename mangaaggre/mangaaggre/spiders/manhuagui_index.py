# -*- coding: utf-8 -*-
import scrapy
from ..manga_enum import MangaIndexTypeEnum
from ..items import MangaIndexItem


class ManhuaguiIndexSpider(scrapy.Spider):
    name = 'manhuagui_index'
    allowed_domains = ['www.manhuagui.com']

    def start_requests(self):
        url = 'https://www.manhuagui.com/comic/' + \
            getattr(self, 'keyword', 'test')
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        def get_type(idx_type):
            if idx_type == '单话':
                type_ = MangaIndexTypeEnum.CHAPTER
            elif idx_type == '单行本':
                type_ = MangaIndexTypeEnum.VOLUME
            else:
                type_ = MangaIndexTypeEnum.MISC
            return type_
        div = response.css('div.chapter')
        idx_types = div.css('h4 span::text').getall()
        divs = div.css('div.chapter-list')
        name = response.css('div.book-title h1::text').get()
        for idx_type, div in zip(idx_types, divs):
            type_ = get_type(idx_type)
            for ul in div.css('ul'):
                for a in reversed(ul.css('a')):
                    title = a.css('::attr(title)').get()
                    url = a.css('::attr(href)').get()
                    if not url.startswith('http'):
                        url = 'https://www.manhuagui.com/' + url.lstrip('/')
                    yield MangaIndexItem(name=name, title=title, type_=type_, url=url)


            

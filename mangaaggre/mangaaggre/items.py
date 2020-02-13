# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Manga(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()

class MangaIndexItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    title = scrapy.Field()
    type_ = scrapy.Field()
    url = scrapy.Field()
    
class MangaChapterItem(scrapy.Item):
    name = scrapy.Field()
    title = scrapy.Field()
    page = scrapy.Field()
    url = scrapy.Field()


class MangaSearchResultItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()

# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
from urllib.parse import urlparse
import pdb

from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request


class MangaaggrePipeline(object):
    def process_item(self, item, spider):
        return item


class MyImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        def create_req(url, idx):
            req = Request(url)
            req.meta['idx'] = idx
            req.meta['dir'] = item.get('dir')
            return req
        return [create_req(x, idx) for idx, x in enumerate(item.get(self.images_urls_field, []))]
    def file_path(self, request, response=None, info=None):
        idx = request.meta['idx']
        folder = request.meta['dir']
        return f'{folder}/{idx}{os.path.splitext(urlparse(request.url).path)[-1]}'

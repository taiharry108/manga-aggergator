# -*- coding: utf-8 -*-
import scrapy
from ..manga_enum import MangaIndexTypeEnum
from ..items import MangaIndexItem, MangaChapterItem
from ..decrypt_mhg import decode, decompress
from urllib import parse
import re
import json
import pdb
import pandas as pd

from scrapy.shell import inspect_response
DOMAIN = 'https://www.manhuagui.com/'


class ManhuaguiChapterSpider(scrapy.Spider):
    name = 'manhuagui_chapter'
    allowed_domains = ['www.manhuagui.com']

    def start_requests(self):
        yield scrapy.Request('https://www.manhuagui.com/comic/4681/186828.html', self.parse)

    def parse(self, response):
        for script in response.css('script'):
            match = script.re('window.*return p;}(.*\))\)')
            if match:
                break
        p, a, c, k, e, d = eval(match[0].replace(
            r"['\x73\x70\x6c\x69\x63']('\x7c')", ""))
        p = decode(p, a, c, decompress(k).split('|'), d)

        match = re.search('SMH.imgData\((.*)\).preInit', p)
        manga_data = json.loads(match.group(1))
        print(match.group(1))
        cid = manga_data['cid']
        path = manga_data['path']
        md5 = manga_data["sl"]["md5"]
        manga_name = manga_data['bname']
        chap_title = manga_data['cname']
        for idx, file in enumerate(manga_data['files']):
            page_url = f"https://i.hamreus.com{path}{file}?cid={cid}&md5={md5}"
            yield MangaChapterItem(name=manga_name,
                                   title=chap_title,
                                   page=idx,
                                   url=page_url)


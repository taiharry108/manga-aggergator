# -*- coding: utf-8 -*-
import scrapy
from ..manga_enum import MangaIndexTypeEnum
from ..items import MangaIndexItem, MangaChapterItem
from ..encryption import decrypt
from urllib import parse
import re
import json
import pdb
import pandas as pd

DOMAIN = 'https://www.manhuadui.com/'


class ManhuaduiChapterSpider(scrapy.Spider):
    name = 'manhuadui_chapter'
    allowed_domains = ['www.manhuadui.com']

    def get_urls(self):
        path = getattr(self, "path", None)
        if path is None:
            csv_file = getattr(self, "csv_file")
            urls = pd.read_csv(csv_file).url.tolist()
        else:
            urls = [path]
        return [DOMAIN + url.lstrip('/') for url in urls]

    def start_requests(self):
        req = scrapy.Request(DOMAIN, self.parse)
        req.meta['urls'] = [
            'https://www.manhuadui.com/manhua/sirenzhentan/459131.html']
        yield req
    
    def decrypt_pages(self, s):
        decrypted = decrypt(s)
        idx = decrypted.find('"]')
        if idx != -1:
            decrypted = decrypted[:idx+2]
            pages = json.loads(decrypted)
        else:
            pages = []
        return pages
                
    
    def parse_chapter(self, response):
        for script in response.css('script'):
            s = 'chapterImages = "(.*)";var chapterPath = "(.*)";var chapterPrice'
            match = script.re(s)

            if len(match) == 2:
                pages = self.decrypt_pages(match[0])
                chap_path = match[1]

        if getattr(self, 'manga_name', None) is None:
            manga_name = response.css('div.head_title a::text').get()
        if getattr(self, 'chap_title', None) is None:
            chap_title = response.css('div.head_title h2::text').get()

        pages = [self.get_page_url(page, chap_path) for page in pages]

        for idx, page_url in enumerate(pages):
            yield MangaChapterItem(name=manga_name,
                                   title=chap_title,
                                   page=idx,
                                   url=page_url)
        # yield {'image_urls': pages, 'dir': f'{manga_name}/{chap_title}'}

    def parse_conf(self, response):
        s = response.text
        match = re.search('resHost: (\[.*\]),\\r\\n', s)
        try:
            matched = match.group(1)
            d = json.loads(matched)
            self.img_domain = d[0]['domain'][0]
        except:
            self.img_domain = "https://mhimg.eshanyao.com"
        print(self.img_domain)
        
        urls = response.meta['urls']
        # urls = self.get_urls()
        for url in urls:
            yield scrapy.Request(url, self.parse_chapter)

    def get_page_url(self, page_url, chap_path):
        print(page_url)
        encodeURI = parse.quote
        if re.search('^https?://(images.dmzj.com|imgsmall.dmzj.com)', page_url):
            return f'{self.img_domain}/showImage.php?url=' + encodeURI(page_url)
        if re.search('^[a-z]/', page_url):
            return f'{self.img_domain}/showImage.php?url=' + encodeURI("https://images.dmzj.com/" + page_url)
        if re.search("^(http:|https:|ftp:|^)//", page_url):
            return page_url
        filename = chap_path + '/' + page_url
        return self.img_domain + '/' + filename

    def parse(self, response):
        for script in response.css('script'):
            src = script.css("::attr(src)").get()
            if src is not None and 'config.js' in src:
                req = scrapy.Request(DOMAIN + src, self.parse_conf)
                req.meta['urls'] = response.meta['urls']
                yield req
                # yield scrapy.Request(DOMAIN + src, self.parse_conf, cb_kwargs={'prev_rep': response})

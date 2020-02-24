from MangaSite import MangaSite
from bs4 import BeautifulSoup
from PySide2 import QtNetwork
from functools import partial
from Manga import Manga, MangaIndexTypeEnum
import re
from Crypto.Cipher import AES
import base64
import json
from urllib import parse
import string
import lzstring
import re
digs = string.digits + string.ascii_letters
QNetworkReply = QtNetwork.QNetworkReply


def decompress(s):
    x = lzstring.LZString()
    return x.decompressFromBase64(s)


def int2base(x, base):
    if x < 0:
        sign = -1
    elif x == 0:
        return digs[0]
    else:
        sign = 1

    x *= sign
    digits = []

    while x:
        digits.append(digs[int(x % base)])
        x = int(x / base)

    if sign < 0:
        digits.append('-')

    digits.reverse()

    return ''.join(digits)


def decode(p, a, c, k, d):
    def e(c):
        first = "" if c < a else e(int(c/a))
        c = c % a
        if c > 35:
            second = chr(c + 29)
        else:
            second = int2base(c, 36)
        return first + second
    while c != 0:
        c -= 1
        d[e(c)] = k[c] if k[c] != "" else e(c)
    k = [lambda x: d[x]]
    def e(): return '\\w+'
    c = 1
    while c != 0:
        c -= 1
        p = re.sub(f'\\b{e()}\\b', lambda x: k[c](x.group()), p)
    return p


class ManHuaGui(MangaSite):
    def __init__(self):
        super(ManHuaGui, self).__init__('漫畫鬼', 'https://www.manhuagui.com/')

    def parse_search_result(self, reply: QNetworkReply, meta_dict: dict):
        def handle_dict(d):
            name = d['t']
            url = d['u']
            if not url.startswith('http'):
                url = 'https://www.manhuagui.com/' + url.lstrip('/')
            manga = self.get_manga(manga_name=name, manga_url=url)
            return manga

        data = reply.readAll().data()
        json_data = json.loads(data)
        result = [handle_dict(d) for d in json_data]
        self.search_result.emit(result)

    def parse_index_result(self, reply: QNetworkReply, meta_dict: dict):
        def get_type(idx_type):
            if idx_type == '单话':
                type_ = MangaIndexTypeEnum.CHAPTER
            elif idx_type == '单行本':
                type_ = MangaIndexTypeEnum.VOLUME
            else:
                type_ = MangaIndexTypeEnum.MISC
            return type_

        data = reply.readAll()
        soup = BeautifulSoup(data.data(), features="html.parser")

        manga_url = reply.url().toString()

        div = soup.find('div', class_='chapter')
        idx_types = [h4.find('span').text for h4 in div.find_all('h4')]
        divs = div.find_all('div', class_='chapter-list')
        name = soup.find('div', class_='book-title').find('h1').text

        manga = self.get_manga(manga_name=name, manga_url=manga_url)

        for idx_type, div in zip(idx_types, divs):
            m_type = get_type(idx_type)
            for ul in div.find_all('ul'):
                for a in reversed(ul.find_all('a')):
                    title = a.get('title')
                    url = a.get('href')
                    if not url.startswith('http'):
                        url = 'https://www.manhuagui.com/' + url.lstrip('/')
                    manga.add_chapter(m_type=m_type, title=title, page_url=url)

        self.index_page.emit(manga)

    def parse_page_urls(self, reply: QNetworkReply, meta_dict: dict):
        data = reply.readAll()
        soup = BeautifulSoup(data.data(), features="html.parser")

        pattern = re.compile('window.*return p;}(.*\))\)')
        for script in soup.find_all('script'):
            match = pattern.search(script.text)
            if match:
                break

        p, a, c, k, e, d = eval(match.group(1).replace(
            r"['\x73\x70\x6c\x69\x63']('\x7c')", ""))
        p = decode(p, a, c, decompress(k).split('|'), d)

        match = re.search('SMH.imgData\((.*)\).preInit', p)
        manga_data = json.loads(match.group(1))
        cid = manga_data['cid']
        path = manga_data['path']
        md5 = manga_data["sl"]["md5"]
        manga_name = manga_data['bname']
        chap_title = manga_data['cname']
        pages = []
        for idx, file in enumerate(manga_data['files']):
            page_url = f"https://i.hamreus.com{path}{file}?cid={cid}&md5={md5}"
            pages.append(page_url)

        self.get_pages_completed.emit(pages, meta_dict['manga'], meta_dict['m_type'], meta_dict['idx'])

    def search_manga(self, keyword):
        search_url = f'{self.url}tools/word.ashx?key={keyword}'
        self.downloader.get_request(search_url, self.parse_search_result)

    def get_index_page(self, page):
        self.downloader.get_request(page, self.parse_index_result)

    def get_page_urls(self, manga: Manga, m_type: MangaIndexTypeEnum, idx: int):
        chapter = manga.get_chapter(m_type, idx)
        chapter_url = chapter.page_url
        self.downloader.get_request(
            chapter_url, self.parse_page_urls, meta_dict={"manga":manga, "m_type":m_type, "idx":idx})

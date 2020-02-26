import string
from MangaSite import MangaSite
from bs4 import BeautifulSoup
from PySide2 import QtNetwork
from functools import partial
from Manga import Manga, MangaIndexTypeEnum
import re
import base64
import json
from urllib import parse
import re
from Downloader import Downloader
QNetworkReply = QtNetwork.QNetworkReply

digs = string.digits + string.ascii_letters


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

class ManHuaRen(MangaSite):
    def __init__(self, downloader: Downloader):
        super(ManHuaRen, self).__init__(
            '漫畫人', 'https://www.manhuaren.com/', downloader)

    def parse_search_result(self, reply: QNetworkReply, meta_dict: dict):
        
        def handle_div(div):
            name = div.find('p', class_='book-list-info-title').text
            url = div.find('a').get('href')
            if not url.startswith('http'):
                url = self.url + url.lstrip('/')
            manga = self.get_manga(manga_name=name, manga_url=url)
            return manga
        
        data = reply.readAll()
        soup = BeautifulSoup(data.data(), features="html.parser")

        result = [handle_div(d) for d in soup.find('ul', class_='book-list').find_all(
            'div', class_='book-list-info')]
        self.search_result.emit(result)
    
    def get_meta_data(self, soup):
        div = soup.find(
            'div', {'id': 'tempc'}).find('div', class_='detail-list-title')
        last_update = div.find(
            'span', class_='detail-list-title-3').text
        finished = div.find('span', class_='detail-list-title-1').text == '已完结'
        thum_img = soup.find('img', class_='detail-main-bg').get('src')

        if not thum_img.startswith('http'):
            thum_img = self.url + thum_img.lstrip('/')
        
        
        return {'last_update':last_update, 'finished': finished, 'thum_img':thum_img}

    def parse_index_result(self, reply: QNetworkReply, meta_dict: dict):
        type_names = {'连载', '单行本', '番外篇'}
        def get_type(idx_type):
            if idx_type == '连载':
                type_ = MangaIndexTypeEnum.CHAPTER
            elif idx_type == '单行本':
                type_ = MangaIndexTypeEnum.VOLUME
            else:
                type_ = MangaIndexTypeEnum.MISC
            return type_

        data = reply.readAll()
        soup = BeautifulSoup(data.data(), features="html.parser")

        manga_url = reply.url().toString()
        name = soup.find('p', class_='detail-main-info-title').text

        div = soup.find('div', class_='detail-selector')

        id_dict = {}

        for a in div.find_all('a', 'detail-selector-item'):
            onclick = a.get('onclick')
            if 'titleSelect' in onclick:
                id_dict[a.text] = onclick.split("'")[3]
        
        manga = self.get_manga(manga_name=name, manga_url=manga_url)

        for idx_type, id_v in id_dict.items():
            ul = soup.find('ul', {'id': id_v})
            m_type = get_type(idx_type)
            for a in ul.find_all('a'):
                url = a.get('href')
                if not url.startswith('http'):
                    url = self.url + url.lstrip('/')
                title = a.text
                manga.add_chapter(m_type=m_type, title=title, page_url=url)

        manga.set_meta_data(self.get_meta_data(soup))
        self.index_page.emit(manga)

    def parse_page_urls(self, reply: QNetworkReply, meta_dict: dict):
        data = reply.readAll()
        soup = BeautifulSoup(data.data(), features="html.parser")

        for script in soup.find_all('script'):
            if script.text.startswith('eval'):
                match = re.search('return p;}(.*\))\)', script.text)
                break
        if match:
            print('match1')
            tuple_str = match.group(1)
            p, a, c, k, e, d = eval(tuple_str)
            p = decode(p, a, c, k, d)
            print(p)

            match2 = re.search(r'var newImgs=(.*);', p)
            if match2:
                print('match2')
                pages = eval(match2.group(1))

                self.get_pages_completed.emit(pages, meta_dict['manga'], meta_dict['m_type'], meta_dict['idx'])

    def search_manga(self, keyword):
        search_url = f'{self.url}search?title={keyword}&language=1'
        self.downloader.get_request(search_url, self.parse_search_result)

    def get_index_page(self, page):
        self.downloader.get_request(page, self.parse_index_result)

    def get_page_urls(self, manga: Manga, m_type: MangaIndexTypeEnum, idx: int):
        chapter = manga.get_chapter(m_type, idx)
        chapter_url = chapter.page_url
        self.downloader.get_request(
            chapter_url, self.parse_page_urls, meta_dict={"manga":manga, "m_type":m_type, "idx":idx})

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


class ManHuaDB(MangaSite):
    def __init__(self, downloader: Downloader):
        super(ManHuaDB, self).__init__(
            '漫畫DB', 'https://www.manhuadb.com/', downloader)

    def parse_search_result(self, reply: QNetworkReply, meta_dict: dict):
        
        def handle_div(div):
            name = div.find('a').get('title')
            url = div.find('a').get('href')
            if not url.startswith('http'):
                url = self.url + url.lstrip('/')
            manga = self.get_manga(manga_name=name, manga_url=url)
            return manga
        
        data = reply.readAll()
        soup = BeautifulSoup(data.data(), features="html.parser")

        result = [handle_div(d) for d in soup.find_all('div', class_='comicbook-index')]
        self.search_result.emit(result)
    
    def get_meta_data(self, soup):
        table = soup.find(
            'table', class_='comic-meta-data-table')
        last_update = None
        finished = table.find('a', class_='comic-pub-state').text != '连载中'
        thum_img = table.find('td', class_='comic-cover').find('img').get('src')

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

        ul = soup.find('ul', {'id': 'myTab'})
        a_list = ul.find_all('a', class_='nav-link')
        id_dict = {a.find('span').text: a.get('aria-controls')
                   for a in a_list if a.find('span').text in type_names}
        name = soup.find('h1', class_='comic-title').text

        manga = self.get_manga(manga_name=name, manga_url=manga_url)

        div = soup.find('div', {'id':'comic-book-list'})

        for idx_type, id_v in id_dict.items():
            tab = div.find('div', {'id':id_v})
            m_type = get_type(idx_type)
            for li in tab.find_all('li'):
                a = li.find('a')
                title = a.get('title')
                url = a.get('href')
                if not url.startswith('http'):
                    url = self.url + url.lstrip('/')
                manga.add_chapter(m_type=m_type, title=title, page_url=url)
        

        manga.set_meta_data(self.get_meta_data(soup))
        self.index_page.emit(manga)

    def parse_page_urls(self, reply: QNetworkReply, meta_dict: dict):
        data = reply.readAll()
        soup = BeautifulSoup(data.data(), features="html.parser")

        pattern = re.compile(r"var img_data = '(.*)'")
        for script in soup.find_all('script'):
            match = pattern.search(script.text)
            if match:
                break

        decoded = base64.b64decode(match.group(1))
        decoded_list = json.loads(decoded)

        vgr_data = soup.find('div', 'vg-r-data')
        host = vgr_data.get('data-host')
        img_pre = vgr_data.get('data-img_pre')
        pages = [f'{host}{img_pre}{d["img_webp"]}' for d in decoded_list]
        

        self.get_pages_completed.emit(pages, meta_dict['manga'], meta_dict['m_type'], meta_dict['idx'])

    def search_manga(self, keyword):
        search_url = f'{self.url}search?q={keyword}'
        self.downloader.get_request(search_url, self.parse_search_result)

    def get_index_page(self, page):
        self.downloader.get_request(page, self.parse_index_result)

    def get_page_urls(self, manga: Manga, m_type: MangaIndexTypeEnum, idx: int):
        chapter = manga.get_chapter(m_type, idx)
        chapter_url = chapter.page_url
        self.downloader.get_request(
            chapter_url, self.parse_page_urls, meta_dict={"manga":manga, "m_type":m_type, "idx":idx})

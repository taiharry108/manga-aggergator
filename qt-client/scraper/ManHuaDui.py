from MangaSite import MangaSite
from bs4 import BeautifulSoup
from PySide2 import QtNetwork, QtCore
from functools import partial
from pathlib import Path
from Manga import Manga, MangaIndexTypeEnum
import re

QNetworkReply = QtNetwork.QNetworkReply
class ManHuaDui(MangaSite):    

    def __init__(self):
        super(ManHuaDui, self).__init__('漫畫堆', 'https://www.manhuadui.com/')
        self.img_domain = None
    
    
    
    def parse_search_result(self, reply: QNetworkReply, meta_dict: dict):
        data = reply.readAll()
        soup = BeautifulSoup(data.data(), features="html.parser")
        result = []
        
        div = soup.find("div", {"id":"w0"})
        lis = div.find_all("li", class_='list-comic')
        for li in lis:
            a = li.find('a', class_='image-link')
            url = a.get('href')
            name = a.get('title')
            manga = self.get_manga(manga_name=name, manga_url=url)
            result.append(manga)
        self.search_result.emit(result)
    
    def parse_index_result(self, reply: QNetworkReply, meta_dict: dict):
        data = reply.readAll()
        soup = BeautifulSoup(data.data(), features="html.parser")
        ul = soup.find('ul', {'id':'chapter-list-1'})
        li_list = ul.find_all('li')
        manga_url = reply.url().toString()

        m_type = MangaIndexTypeEnum.CHAPTER
        name = soup.find('div', class_='comic_deCon').find('h1').text
        manga = self.get_manga(manga_name=name, manga_url=manga_url)
        for li in li_list:
            url = li.a.get('href').lstrip('/')
            if not url.startswith('http'):
                url = 'https://www.manhuadui.com/' + url
            title = li.a.get('title')
            manga.add_chapter(m_type=m_type, title=title, page_url=url)

        self.index_page.emit(manga)
    
    
    
    def parse_page_urls(self, reply: QNetworkReply, meta_dict: dict):
        pass

    def search_manga(self, keyword):
        search_url = f'{self.url}search/?keywords={keyword}'
        self.downloader.get_request(search_url, self.parse_search_result)
        

    def get_index_page(self, page):
        self.downloader.get_request(page, self.parse_index_result)
    
    def parse_conf(self, reply: QNetworkReply, meta_dict: dict):
        s = str(reply.readAll().data)
        match = re.search('resHost: (\[.*\]),\\r\\n', s)
        try:
            matched = match.group(1)
            d = json.loads(matched)
            self.img_domain = d[0]['domain'][0]
        except:
            self.img_domain = "https://mhimg.eshanyao.com"
        
    
    def parse(self, reply: QNetworkReply, meta_dict: dict):
        data = reply.readAll()
        soup = BeautifulSoup(data.data(), features="html.parser")
        scripts = soup.find_all('script')
        for script in scripts:
            src = script.get('src')
            if src is not None and 'config.js' in src:
                url = self.url + src.lstrip('/')
                self.downloader.get_request(url, self.parse_conf)
        
    
    def get_img_domain(self):
        self.downloader.get_request(self.url, self.parse)

    def get_page_urls(self, chapter_url):
        if self.img_domain is not None:
            self.downloader.get_request(chapter_url, self.parse_page_urls)
        else:
            self.get_img_domain()
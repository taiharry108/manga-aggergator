from MangaSite import MangaSite
from bs4 import BeautifulSoup
from PySide2 import QtNetwork, QtCore
from functools import partial
from pathlib import Path
from Manga import Manga, MangaIndexTypeEnum
import re
from Crypto.Cipher import AES
import base64
import json
from urllib import parse
from Downloader import Downloader

def decrypt(encrypted) -> str:
    encrypted = base64.b64decode(encrypted)
    passphrase = "123456781234567G"
    iv = "ABCDEF1G34123412"
    aes = AES.new(passphrase, AES.MODE_CBC, iv)

    decrypted = aes.decrypt(encrypted)
    return decrypted.strip().decode('utf8')


def decrypt_pages(s):
    decrypted = decrypt(s)
    idx = decrypted.find('"]')
    if idx != -1:
        decrypted = decrypted[:idx+2]
        pages = json.loads(decrypted)
    else:
        pages = []
    return pages

QNetworkReply = QtNetwork.QNetworkReply
class ManHuaDui(MangaSite):    

    def __init__(self, downloader: Downloader):
        super(ManHuaDui, self).__init__('漫畫堆', 'https://www.manhuadui.com/', downloader)
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
        
        last_update = soup.find('span', class_='zj_list_head_dat')
        if last_update is not None:
            match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', last_update.text)
            if match:
                last_update = match.group(0)
        
        finished = soup.find('ul', class_='comic_deCon_liO').find('a', {'href':'/list/wanjie/'}) is not None
        
        manga.set_meta_data({'last_update':last_update, 'finished': finished})

        self.index_page.emit(manga)
    
    def get_page_url(self, page_url, chap_path):
        encodeURI = parse.quote
        if re.search('^https?://(images.dmzj.com|imgsmall.dmzj.com)', page_url):
            return f'{self.img_domain}/showImage.php?url=' + encodeURI(page_url)
        if re.search('^[a-z]/', page_url):
            return f'{self.img_domain}/showImage.php?url=' + encodeURI("https://images.dmzj.com/" + page_url)
        if re.search("^(http:|https:|ftp:|^)//", page_url):
            return page_url
        filename = chap_path + '/' + page_url
        return self.img_domain + '/' + filename
    
    def parse_page_urls(self, reply: QNetworkReply, meta_dict: dict):
        data = reply.readAll()
        soup = BeautifulSoup(data.data(), features="html.parser")

        pattern = re.compile(
            'chapterImages = "(.*)";var chapterPath = "(.*)";var chapterPrice')
        for script in soup.find_all('script'):
            match = pattern.search(script.text)
            if match:
                break

        pages = decrypt_pages(match.group(1))
        chap_path = match.group(2)

        pages = [self.get_page_url(page, chap_path) for page in pages]

        self.get_pages_completed.emit(pages, meta_dict['manga'], meta_dict['m_type'], meta_dict['idx'])


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
        
        if "chapter_url" in meta_dict.keys():
            self.downloader.get_request(
                meta_dict['chapter_url'], self.parse_page_urls, meta_dict=meta_dict)
        
    
    def parse(self, reply: QNetworkReply, meta_dict: dict):
        data = reply.readAll()
        soup = BeautifulSoup(data.data(), features="html.parser")
        scripts = soup.find_all('script')
        for script in scripts:
            src = script.get('src')
            if src is not None and 'config.js' in src:
                url = self.url + src.lstrip('/')
                self.downloader.get_request(url, self.parse_conf, meta_dict=meta_dict)
        
    
    def get_img_domain(self, meta_dict):
        self.downloader.get_request(self.url, self.parse, meta_dict=meta_dict)

    def get_page_urls(self, manga: Manga, m_type: MangaIndexTypeEnum, idx: int):
        chapter = manga.get_chapter(m_type, idx)
        chapter_url = chapter.page_url
        if self.img_domain is not None:
            self.downloader.get_request(
                chapter_url, self.parse_page_urls, meta_dict={"manga":manga, "m_type":m_type, "idx":idx})
        else:
            self.get_img_domain(meta_dict={"chapter_url": chapter_url, "manga":manga, "m_type":m_type, "idx":idx})

from PySide2 import QtWidgets, QtCore
import requests
import mimetypes
import shutil
from pathlib import Path
from ApiResultModel import ApiResultModelStatus
from enum import Enum


class MangaSiteEnum(Enum):
    MANHUADUI = "漫畫堆"
    MANHUAGUI = "漫畫鬼"


class MangaAggreController(object):
    def __init__(self):
        self.setMangaSite(0)

    def setMangaSite(self, idx):
        self.mangaSite = list(MangaSiteEnum)[idx]

    def _call_api(self, url, spider, meta=None):
        data = {
            "request": {"url": url}, "spider_name": spider
        }
        if meta is not None:
            data["request"]['meta'] = meta
        r = requests.post('http://localhost:9080/crawl.json', json=data)
        result = r.json()
        if result['status'] != 'ok':
            raise Exception
        else:
            return result['items']

    def searchManga(self, keyword: str, new_status: ApiResultModelStatus):
        if self.mangaSite == MangaSiteEnum.MANHUADUI:
            url = f"https://www.manhuadui.com/search/?keywords={keyword}"
            spider = "manhuadui_search"

        elif self.mangaSite == MangaSiteEnum.MANHUAGUI:
            url = f'https://www.manhuagui.com/tools/word.ashx?key={keyword}'
            spider = "manhuagui_search"

        return self._call_api(url, spider), new_status

    def getChapters(self, url: str, new_status: ApiResultModelStatus):
        if self.mangaSite == MangaSiteEnum.MANHUADUI:
            spider = "manhuadui_index"
        elif self.mangaSite == MangaSiteEnum.MANHUAGUI:
            spider = "manhuagui_index"
        return self._call_api(url, spider), new_status

    def getPages(self, url: str, new_status: ApiResultModelStatus):
        if self.mangaSite == MangaSiteEnum.MANHUADUI:
            spider = "manhuadui_chapter"
        elif self.mangaSite == MangaSiteEnum.MANHUAGUI:
            spider = "manhuagui_chapter"
        return self._call_api(url, spider, meta={'urls': [url]}), new_status

    def downloadPage(self, filename: Path, url: str, referer=None):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        }
        if referer is not None:
            headers['Referer'] = referer

            
        r = requests.get(url, stream=True, headers=headers)
        if r.status_code == 200:
            content_type = r.headers['content-type']
            if content_type.startswith('image/webp'):
                extension = '.webp'
            else:
                extension = mimetypes.guess_extension(content_type)
            with open(filename.with_suffix(extension), 'wb') as f:
                shutil.copyfileobj(r.raw, f)
                return True
        else:
            return False


if __name__ == "__main__":
    ctr = MangaAggreController()
    print(ctr.getPages(
        "https://www.manhuadui.com/manhua/guimiezhiren/445567.html", "1"))

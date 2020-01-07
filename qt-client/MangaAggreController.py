from PySide2 import QtWidgets, QtCore
import requests
import mimetypes
import shutil
from pathlib import Path
from ApiResultModel import ApiResultModelStatus


class MangaAggreController(object):
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
        url = "https://www.manhuadui.com/search/?keywords=" + keyword
        spider = "manhuadui_search"

        return self._call_api(url, spider), new_status

    def getChapters(self, url: str, new_status: ApiResultModelStatus):
        spider = "manhuadui_index"
        return self._call_api(url, spider), new_status

    def getPages(self, url: str, new_status: ApiResultModelStatus):
        spider = "manhuadui_chapter"
        return self._call_api(url, spider, meta={'urls': [url]}), new_status

    def downloadPage(self, filename: Path, url: str):
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            content_type = r.headers['content-type']
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

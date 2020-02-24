from enum import Enum
from ManHuaDui import ManHuaDui
from ManHuaGui import ManHuaGui
from MangaSite import MangaSite
from Downloader import Downloader

class MangaSiteEnum(Enum):
    ManHuaDui = "漫畫堆"
    ManHuaGui = "漫畫鬼"

def get_manga_site(manga_site_enum: MangaSiteEnum, downloader: Downloader) -> MangaSite:
    if manga_site_enum == MangaSiteEnum.ManHuaDui:
        return ManHuaDui(downloader)
    elif manga_site_enum == MangaSiteEnum.ManHuaGui:
        return ManHuaGui(downloader)

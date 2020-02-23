from enum import Enum
from ManHuaDui import ManHuaDui
from ManHuaGui import ManHuaGui
from MangaSite import MangaSite

class MangaSiteEnum(Enum):
    ManHuaDui = 1
    ManHuaGui = 2

def get_manga_site(manga_site_enum: MangaSiteEnum) -> MangaSite:
    if manga_site_enum == MangaSiteEnum.ManHuaDui:
        return ManHuaDui()
    elif manga_site_enum == MangaSiteEnum.ManHuaGui:
        return ManHuaGui()

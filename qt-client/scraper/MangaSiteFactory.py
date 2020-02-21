from enum import Enum
from ManHuaDui import ManHuaDui
from MangaSite import MangaSite

class MangaSiteEnum(Enum):
    ManHuaDui = 1

def get_manga_site(manga_site_enum: MangaSiteEnum) -> MangaSite:
    if manga_site_enum == MangaSiteEnum.ManHuaDui:
        return ManHuaDui()

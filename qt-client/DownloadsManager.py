class DownloadsManager(object):
    def __init__(self, root):
        self.root = root
        self.data = {}
    def check_downloads(self, name):
        manga_dir = self.root/name
        if manga_dir.is_dir():
            self.data[name] = [(chap_dir.name, len(list(chap_dir.iterdir()))) for chap_dir in manga_dir.iterdir()]



if __name__ == "__main__":
    from pathlib import Path
    root = Path('./downloads')
    manager = DownloadsManager(root)
    manager.check_downloads('鬼灭之刃')
    print(manager.data)

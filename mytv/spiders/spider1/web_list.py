import unittest
import re
from ..utils import get_soup_from_url
from show.models import Show
from .web_show import WebShow


class WebList:
    def __init__(self, page_num):
        self.page_num = page_num
        self._url = f'list-{self.page_num}.htm'
        self._soup = None
        self._data = None

    @staticmethod
    def get_max_page_num(url='list.htm'):
        soup = get_soup_from_url(url)
        txt = soup.select('ul.pagination1 > li > a')[-2].get_text()
        return int(txt.replace('.', ''))

    @classmethod
    def update_shows_in_all_pages_incremental(cls):
        start_page = cls.get_max_page_num()  # cls.get_first_no_cache_page()
        for num in range(start_page, 0, -1):
            print(f'saving page {num}')
            page = WebList(num)
            try:
                page.save_shows_in_this_page()
            except:
                pass

    @classmethod
    def get_first_no_cache_page(cls):
        max_page_num = cls.get_max_page_num()

        lo, hi = 0, max_page_num

        while lo + 1 < hi:
            mid = (lo + hi) // 2
            if WebList(mid).all_shows_in_db():
                hi = mid
            else:
                lo = mid
        return min(hi + 5, max_page_num)

    def soup(self):
        if self._soup is not None: return self._soup
        self._soup = get_soup_from_url(self._url)
        return self._soup

    def get_show_id_list(self):
        soup = self.soup()
        shows = soup.select('div.caption.title > h5 > a')
        shows = [s.get('href') for s in shows]
        shows = [re.findall(r'\b\d+\b', s)[-1] for s in shows]
        return [int(s) for s in shows]

    def shows_not_in_db(self):
        shows = self.get_show_id_list()
        return [sid for sid in shows if not Show.objects.filter(show_id=sid).exists()]

    def all_shows_in_db(self):
        return not bool(self.shows_not_in_db())

    def save_shows_in_this_page(self):
        shows_to_save = self.shows_not_in_db()
        for sid in shows_to_save:
            ws = WebShow(show_id=sid)
            ws.save()

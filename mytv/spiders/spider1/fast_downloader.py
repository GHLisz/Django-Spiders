# This is a standalone script that can be deleted without hurting anything
# It's meant to help exhausting this site,
# by down all list pages at once to avoid missing items caused by site updating.

import os
from multiprocessing.pool import ThreadPool

import requests
from bs4 import BeautifulSoup

from .web_list import WebList
from .web_show import WebShow
from show.models import Show

URL_HOST = ''
LOCAL_PATH = r''
THREAD_COUNT = 5


class StandaloneUtils:

    @staticmethod
    def get_files_recursively(root_dir):
        print('root dir is: ', root_dir)
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                yield os.path.join(root, file)

    @staticmethod
    def down_a_page(url, full_file_name):
        print(f'job received: from {url} to {full_file_name}')

        dirname = os.path.dirname(full_file_name)
        os.makedirs(dirname, exist_ok=True)

        try:
            r = requests.get(url, timeout=60)
            with open(full_file_name, 'wb') as f:
                f.write(r.content)
        except Exception:
            pass

    @staticmethod
    def get_soup_from_url(url):
        wb_data = requests.get(url, timeout=5)
        wb_data.encoding = 'utf8'
        soup = BeautifulSoup(wb_data.text, 'html5lib')
        return soup

    @staticmethod
    def get_max_page_num(url='list.htm'):
        soup = StandaloneUtils.get_soup_from_url(URL_HOST + url)
        txt = soup.select('ul.pagination1 > li > a')[-2].get_text()
        return int(txt.replace('.', ''))

    @staticmethod
    def down_pages(page_num_list):
        urls = (f'{URL_HOST}list-{i}.htm' for i in page_num_list)
        files = (f'{LOCAL_PATH}{i}.htm' for i in page_num_list)

        with ThreadPool(THREAD_COUNT) as p:
            p.starmap(StandaloneUtils.down_a_page, zip(urls, files))

    @staticmethod
    def down_all_pages():
        max_page_num = StandaloneUtils.get_max_page_num()
        StandaloneUtils.down_pages(list(range(1, max_page_num + 1)))

        while True:
            deleted = StandaloneUtils.clean_false_files()
            if not deleted:
                break
            StandaloneUtils.down_pages(list(deleted))

    @staticmethod
    def clean_false_files():
        deleted_page_nums = []

        for fn in StandaloneUtils.get_files_recursively(LOCAL_PATH):
            size_kb = os.stat(fn).st_size / 1024
            if size_kb < 15:
                page_num = os.path.splitext(os.path.basename(fn))[0]
                deleted_page_nums.append(page_num)
                os.remove(fn)
        print(f'deleted: {deleted_page_nums}')
        return deleted_page_nums


def get_show_id_list_of_a_file(fn):
    print(f'processing {fn}')
    page_num = os.path.splitext(os.path.basename(fn))[0]
    soup = BeautifulSoup(open(fn, encoding='utf8'), 'html5lib')
    web_list_obj = WebList(page_num=page_num)
    web_list_obj._soup = soup
    return web_list_obj.get_show_id_list()


def save_to_db_of_all_files():
    shows_in_db = (s.show_id for s in Show.objects.all())

    shows_in_files = []
    for fn in StandaloneUtils.get_files_recursively(LOCAL_PATH):
        shows_in_files.extend(get_show_id_list_of_a_file(fn))

    shows_not_in_db = set(shows_in_files) - set(shows_in_db)
    print(shows_not_in_db)
    print(len(shows_not_in_db))
    for sid in shows_not_in_db:
        ws = WebShow(show_id=sid)
        ws.save()


if __name__ == '__main__':
    # StandaloneUtils.down_all_pages()
    # save_to_db_of_all_files()
    pass

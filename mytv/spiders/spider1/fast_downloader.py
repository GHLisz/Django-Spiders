# This is a standalone script that can be deleted without hurting anything
# It's meant to help exhausting this site,
# by down all list pages at once to avoid missing items caused by site updating.

import os
import time
import timeit
from datetime import datetime
from multiprocessing.pool import ThreadPool

import requests
from bs4 import BeautifulSoup

from .web_list import WebList
from .web_show import WebShow
from show.models import Show
from django.conf import settings

URL_HOST = settings.CDN_HOST
LOCAL_PATH_LIST = r''
LOCAL_PATH_SHOW = r''
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
        print(datetime.now(), f'job received: from {url} to {full_file_name}')

        if os.path.exists(full_file_name):
            return

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
        wb_data = requests.get(url, timeout=60)
        wb_data.encoding = 'utf8'
        soup = BeautifulSoup(wb_data.text, 'html5lib')
        return soup

    @staticmethod
    def clean_false_files(path):
        deleted_page_nums = []

        for fn in StandaloneUtils.get_files_recursively(path):
            size_kb = os.stat(fn).st_size / 1024
            if size_kb < 7:
                page_num = os.path.splitext(os.path.basename(fn))[0]
                deleted_page_nums.append(page_num)
                os.remove(fn)
        print(f'deleted: {deleted_page_nums}')
        return deleted_page_nums


class ListUtils:
    @staticmethod
    def get_max_page_num(url='list.htm'):
        soup = StandaloneUtils.get_soup_from_url(URL_HOST + url)
        txt = soup.select('ul.pagination1 > li > a')[-2].get_text()
        return int(txt.replace('.', ''))

    @staticmethod
    def down_pages_of_list(page_num_list):
        urls = (f'{URL_HOST}list-{i}.htm' for i in page_num_list)
        files = (f'{LOCAL_PATH_LIST}{i}.htm' for i in page_num_list)

        with ThreadPool(THREAD_COUNT) as p:
            p.starmap(StandaloneUtils.down_a_page, zip(urls, files))

    @staticmethod
    def down_all_pages_of_list():
        max_page_num = ListUtils.get_max_page_num()
        ListUtils.down_pages_of_list(list(range(1, max_page_num + 1)))

        while True:
            deleted = StandaloneUtils.clean_false_files(LOCAL_PATH_LIST)
            if not deleted:
                break
            ListUtils.down_pages_of_list(list(deleted))


class ShowUtils:
    @staticmethod
    def down_pages_of_show(show_num_list):
        urls = (f'{URL_HOST}video-{i}.htm' for i in show_num_list)
        files = (f'{LOCAL_PATH_SHOW}{i}.htm' for i in show_num_list)

        with ThreadPool(THREAD_COUNT) as p:
            p.starmap(StandaloneUtils.down_a_page, zip(urls, files))

    @staticmethod
    def down_all_pages_of_show(show_num_list):
        ShowUtils.down_pages_of_show(show_num_list)

        while True:
            deleted = StandaloneUtils.clean_false_files(LOCAL_PATH_SHOW)
            if not deleted:
                break
            ShowUtils.down_pages_of_show(list(deleted))

    @staticmethod
    def get_show_id_list_of_a_file(fn):
        print(f'get_show_id_list_of_a_file: {fn}')
        fake_id = 1
        soup = BeautifulSoup(open(fn, encoding='utf8'), 'html5lib')
        web_list_obj = WebList(page_num=fake_id, soup=soup)
        return web_list_obj.get_show_id_list()

    @staticmethod
    def get_all_shows(file_path):
        shows_in_files = []
        for fn in StandaloneUtils.get_files_recursively(file_path):
            shows_in_files.extend(ShowUtils.get_show_id_list_of_a_file(fn))

        # file_list = list(StandaloneUtils.get_files_recursively(file_path))
        # with ThreadPool(200) as p:
        #     shows_in_files = p.map(ShowUtils.get_show_id_list_of_a_file, file_list)

        shows_in_db = (s.show_id for s in Show.objects.all())
        shows_not_in_db = set(shows_in_files) - set(shows_in_db)

        ShowUtils.down_all_pages_of_show(list(shows_not_in_db))

    @staticmethod
    def save_all_shows():
        for fn in StandaloneUtils.get_files_recursively(LOCAL_PATH_SHOW):
            show_id = os.path.splitext(os.path.basename(fn))[0]
            soup = BeautifulSoup(open(fn, encoding='utf8'), 'html5lib')
            show = WebShow(show_id=show_id, soup=soup)
            show.save()


def down_all():
    ListUtils.down_all_pages_of_list()

    ShowUtils.get_all_shows(LOCAL_PATH_LIST)
    ShowUtils.save_all_shows()
    # save ids not in list but in shows
    ShowUtils.get_all_shows(LOCAL_PATH_SHOW)
    ShowUtils.save_all_shows()


if __name__ == '__main__':
    pass

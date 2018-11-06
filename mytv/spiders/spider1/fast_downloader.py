# This is a standalone script that can be deleted without hurting anything
# It's meant to help exhausting this site,
# by down all list pages at once to avoid missing items caused by site updating.

import itertools
import os
import time
import traceback
from datetime import datetime
from multiprocessing.pool import ThreadPool, Pool

import requests
from bs4 import BeautifulSoup
from django.conf import settings

from client.client import down_helper as video_down_helper
from client.client2 import down_helper as image_down_helper
from show.models import Show
from .web_list import WebList
from .web_show import WebShow

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

        prev_deleted = None
        while True:
            deleted = StandaloneUtils.clean_false_files(LOCAL_PATH_SHOW)
            if not deleted or deleted == prev_deleted:
                break
            ShowUtils.down_pages_of_show(list(deleted))
            prev_deleted = deleted

    @staticmethod
    def get_show_id_list_of_a_file(fn):
        print(datetime.now(), f'get_show_id_list_of_a_file: {fn}')
        fake_id = 1
        soup = BeautifulSoup(open(fn, encoding='utf8'), 'html5lib')
        web_list_obj = WebList(page_num=fake_id, soup=soup)
        return web_list_obj.get_show_id_list()

    @staticmethod
    def get_all_shows(file_path):
        file_list = list(StandaloneUtils.get_files_recursively(file_path))
        with Pool() as p:
            shows_in_files = p.map(ShowUtils.get_show_id_list_of_a_file, file_list)
        shows_in_files = list(set(itertools.chain.from_iterable(shows_in_files)))

        with open('d:/get_all_shows.txt', 'w', encoding='utf8') as f:
            for s in shows_in_files:
                f.writelines(str(s) + '\n')

        shows_in_db = (s.show_id for s in Show.objects.all())
        shows_not_in_db = set(shows_in_files) - set(shows_in_db)

        ShowUtils.down_all_pages_of_show(list(shows_not_in_db))

    @staticmethod
    def save_a_show(fn):
        show_id = os.path.splitext(os.path.basename(fn))[0]
        soup = BeautifulSoup(open(fn, encoding='utf8'), 'lxml')
        show = WebShow(show_id=show_id, soup=soup)
        show.save()

    @staticmethod
    def save_all_shows():
        file_list = list(StandaloneUtils.get_files_recursively(LOCAL_PATH_SHOW))

        shows_in_db = [s.show_id for s in Show.objects.all()]
        shows_in_file = [int(os.path.splitext(os.path.basename(fn))[0]) for fn in file_list]
        shows_to_save = set(shows_in_file) - set(shows_in_db)

        shows_to_save_file_list = [p for sid, p in zip(shows_in_file, file_list) if sid in shows_to_save]

        with Pool(1) as p:
            p.map(ShowUtils.save_a_show, shows_to_save_file_list)


class ShowBinary:
    @staticmethod
    def down_video():
        error_count = 0
        while True:
            try:
                jobs = Show.get_down_video_job()
                if not jobs:
                    break
                failed_jobs, passed_jobs = video_down_helper(jobs)
                Show.process_down_video_result(failed_jobs, passed_jobs)
            except Exception as e:
                print(datetime.now())
                error_count += 1
                traceback.print_exc()
                time.sleep(5 * error_count)

    @staticmethod
    def down_image():
        error_count = 0
        while True:
            try:
                jobs = Show.get_down_image_job()
                if not jobs:
                    break
                failed_jobs, passed_jobs = image_down_helper(jobs)
                Show.process_down_image_result(failed_jobs, passed_jobs)
            except Exception as e:
                print(datetime.now())
                error_count += 1
                traceback.print_exc()
                time.sleep(5 * error_count)


def down_all():
    # ListUtils.down_all_pages_of_list()

    # ShowUtils.get_all_shows(LOCAL_PATH_LIST)
    # ShowUtils.save_all_shows()
    # save ids not in list but in shows
    # ShowUtils.get_all_shows(LOCAL_PATH_SHOW)
    # ShowUtils.save_all_shows()
    ShowBinary.down_video()


if __name__ == '__main__':
    pass

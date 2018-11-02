# DJANGO ENVIRON SETUP
import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mytv.settings')
django.setup()

# script starts
import datetime
from show.models import Show
from django.conf import settings


def get_files_recursively(root_dir):
    print('root dir is: ', root_dir)
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            yield os.path.join(root, file)


def main_update_db_from_scratch():
    clear_all_cached_flag()

    for fn in get_files_recursively(settings.VIDEO_CACHE):
        cache_link = settings.VIDEO_CDN_ORIGINAL + os.path.basename(fn)
        for s in Show.objects.filter(video=cache_link):
            print(s)
            s.video_cached = True
            s.save()

    for fn in get_files_recursively(settings.IMAGE_CACHE):
        cache_link = settings.IMAGE_CDN_ORIGINAL + os.path.basename(fn)
        for s in Show.objects.filter(image=cache_link):
            print(s)
            s.image_cached = True
            s.save()


def main_update_db_incremental():
    for s in Show.objects.filter(video_cached=False):
        if os.path.exists(s.video_cache_path):
            s.video_cached = True
            s.save()

    for s in Show.objects.filter(image_cached=False):
        if os.path.exists(s.image_cache_path):
            s.video_cached = True
            s.save()


def clear_all_cached_flag():
    cached_shows = Show.objects.filter()
    r = cached_shows.update(video_cached=False, video_update_time=datetime.datetime(2000, 1, 1),
                            image_cached=False, image_update_time=datetime.datetime(2000, 1, 1))
    print(r)


def diff_tools():
    with open('d:/tmp/tvtmp.txt', 'w', encoding='utf8') as f:
        for s in Show.objects.all():
            f.writelines(str(s.show_id) + '\n')

    # tvset = set(line.strip() for line in open('d:/tmp/tv.txt', encoding='utf8'))
    # tvtmpset = set(line.strip() for line in open('d:/tmp/tvtmp.txt', encoding='utf8'))
    #
    # print('tv added: ', tvset - tvtmpset)
    # print(*sorted(map(int, tvset - tvtmpset)), sep='\n')
    # print('tvtmp added: ', tvtmpset - tvset)
    #
    # with open('d:/tmp/diff.txt', 'w', encoding='utf8') as f:
    #     for s in tvset - tvtmpset:
    #         f.writelines(str(s) + '\n')


def find_cache_file():
    cached = 0
    count = 0
    with open('d:/tmp/diff.txt', encoding='utf8') as f:
        for s in f.readlines():
            sid = int(s)
            show = Show.objects.get(show_id=sid)
            cache_file = show.video_cache_path
            count += 1
            if os.path.exists(cache_file):
                print(show)
                print(cache_file)
                cached += 1
    print(cached)
    print(count)


if __name__ == '__main__':
    diff_tools()

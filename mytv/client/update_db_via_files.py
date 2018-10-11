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

CACHE_PATH = r''
CACHE_PREFIX = ''


def get_files_recursively(root_dir):
    # file_list = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            # file_list.append(os.path.join(root, file))
            yield os.path.join(root, file)
    # return file_list


def main():
    clear_all_cached_flag()
    for fn in get_files_recursively(CACHE_PATH):
        cache_link = CACHE_PREFIX + os.path.basename(fn)
        for s in Show.objects.filter(video=cache_link):
            print(s)
            s.video_cached = True
            s.save()


def peek_data():
    cached_shows = Show.objects.filter(video_cached=False)
    # print(len(cached_shows))
    for s in cached_shows:
        print(s.show_id)


def clear_all_cached_flag():
    cached_shows = Show.objects.filter()
    r = cached_shows.update(video_cached=False, video_update_time=datetime.datetime(2000, 1, 1))
    print(r)


if __name__ == '__main__':
    main()

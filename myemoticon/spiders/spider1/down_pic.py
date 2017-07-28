import os
import sys
import urllib.request
import socket
from time import sleep
from multiprocessing.pool import ThreadPool
from emoticon.models import Photo
from spiders.configs import pic_root_folder

socket.setdefaulttimeout(300)


def save_web_pic_to(pic_url, pic_path):
    print('Downloading: ' + pic_url)
    try:
        urllib.request.urlretrieve(pic_url, pic_path)
        return True
    except:
        sleep(120)
        print(sys.exc_info())
        return False


def save_pic_with_bk(pic_url, pic_path, bk_pic_url=None):
    pic_folder = os.path.dirname(pic_path)
    os.makedirs(pic_folder, exist_ok=True)
    if os.path.exists(pic_path):
        return

    r = save_web_pic_to(pic_url, pic_path)
    if (not r) and bk_pic_url:
        save_web_pic_to(bk_pic_url, pic_path)


def get_pic_args():
    photos = Photo.objects.filter(cached=False)
    for photo in photos:
        pic_url = photo.old_url if photo.old_url.startswith('http:') else 'http:' + photo.old_url
        bk_pic_url = photo.bk_url if photo.bk_url.startswith('http:') else 'http:' + photo.bk_url
        pic_path = pic_root_folder + '/' + \
                   '/'.join(bk_pic_url.
                            replace('http://', '').
                            split('/')[1:])
        yield (pic_url, pic_path, bk_pic_url)


def save_pic_wrapper(args):
    print(args)
    return save_pic_with_bk(*args)


def save_pic_job_multi():
    pool = ThreadPool(4)
    pool.map(save_pic_wrapper, get_pic_args())


if __name__ == '__main__':
    for i in get_pic_args():
        print(i)
        print(type(i))

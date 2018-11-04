# DJANGO ENVIRON SETUP
import os
import sys

import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mytv.settings')
django.setup()

# script starts
import lzma
import json
import base64
from datetime import datetime
from pprint import pprint
from multiprocessing.pool import Pool
from show.models import Show

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
backup_file_name = (os.path.join(BASE_DIR, 'bk.db'))

KEY_ATTRS = ['show_id', 'type', 'url', 'name', 'image', 'video_class', 'actor', 'video', 'duration',
             'upload_date', 'content_location', 'description', 'image_cached', 'video_cached', ]


class CryptBox:
    def __init__(self, file_name):
        self.file_name = file_name
        path = os.path.dirname(self.file_name)
        os.makedirs(path, exist_ok=True)

    def encode_obj(self, obj):
        text = json.dumps(obj)
        self._encode_text(text)

    def decoded_obj(self):
        text = self._decoded_text()
        return json.loads(text)

    def _encode_text(self, text):
        encoded = base64.b85encode(bytes(text, encoding='utf-8'))
        with lzma.open(self.file_name, 'wb') as f:
            f.write(encoded)

    def _decoded_text(self):
        with lzma.open(self.file_name, 'rb') as f:
            encoded = f.read()
        decoded = base64.b85decode(encoded)
        text = str(decoded, encoding='utf-8')
        return text


def backup_db():
    res = [{k: getattr(s, k) for k in KEY_ATTRS} for s in Show.objects.all()]
    cb = CryptBox(backup_file_name)
    cb.encode_obj(res)


def restore_db_incrementally():
    cb = CryptBox(backup_file_name)
    instance_list_in_file = cb.decoded_obj()
    pprint(instance_list_in_file)

    shows_in_db = set(s.show_id for s in Show.objects.all())
    shows_in_file = set(s['show_id'] for s in instance_list_in_file)
    shows_not_in_db = shows_in_file - shows_in_db

    for it in instance_list_in_file:
        if it['show_id'] in shows_not_in_db:
            show = Show(**{k: it[k] for k in KEY_ATTRS})
            show.save()
            pprint(show.__dict__)


def db_bk_diff_helper(sbk):
    sdbs = Show.objects.filter(show_id=sbk['show_id'])
    if sdbs.exists():
        for sdb in sdbs:
            actor_same = sbk['actor'] == sdb.actor
            name_same = sbk['name'] == sdb.name
            image_same = sdb.image_basename in sbk['image']
            video_same = sdb.video_basesname in sbk['video']
            if not all([actor_same, name_same, image_same, video_same]):
                pprint(sbk)
                pprint('----------')
                pprint(sdb.__dict__)
                pprint('#######################')


def db_bk_diff():
    cb = CryptBox(backup_file_name)
    instance_list_in_file = cb.decoded_obj()

    with Pool() as p:
        p.map(db_bk_diff_helper, instance_list_in_file)


def correct_faults():
    cb = CryptBox((os.path.join(BASE_DIR, 'bk.db')))
    cb1 = CryptBox((os.path.join(BASE_DIR, 'bk1.db')))
    cb_dic = {v['show_id']: v for v in cb.decoded_obj()}
    cb1_dic = {v['show_id']: v for v in cb1.decoded_obj()}

    for s in Show.objects.filter(actor=''):
        pprint(s.__dict__)
        actor = cb_dic.get(s.show_id, {}).get('actor', '') or cb1_dic.get(s.show_id, {}).get('actor', '')
        print('---------------')
        if actor:
            print(actor)
            s.actor = actor
            s.save()
        print('###############')

    print('$$$$$$$$$$$$$$')
    for s in Show.objects.filter(name=''):
        pprint(s.__dict__)
        name = cb_dic.get(s.show_id, {}).get('name', '') or cb1_dic.get(s.show_id, {}).get('name', '')
        print('---------------')
        if name:
            print(name)
            s.name = name
            s.save()
        print('###############')


if __name__ == '__main__':
    start = datetime.now()
    backup_db()
    print('time elapsed: ', datetime.now() - start)
    pass

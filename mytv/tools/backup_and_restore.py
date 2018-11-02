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
from pprint import pprint
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
    # pprint(instance_list_in_file)

    shows_in_db = set(s.show_id for s in Show.objects.all())
    shows_in_file = set(s['show_id'] for s in instance_list_in_file)
    shows_not_in_db = shows_in_file - shows_in_db

    for it in instance_list_in_file:
        if it['show_id'] in shows_not_in_db:
            show = Show(**{k: it[k] for k in KEY_ATTRS})
            show.save()
            pprint(show.__dict__)


if __name__ == '__main__':
    # backup_db()
    restore_db_incrementally()
    pass

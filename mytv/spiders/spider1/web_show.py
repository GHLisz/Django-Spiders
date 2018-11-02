import unittest
import re
from bs4 import BeautifulSoup
from datetime import datetime
from spiders.utils import get_soup_from_url
from show.models import Show


class WebShow:
    def __init__(self, show_id, soup=None):
        self.show_id = show_id
        self._url = f'video-{self.show_id}.htm'
        self._soup = soup
        self._data = None

    def soup(self):
        if self._soup is not None: return self._soup
        self._soup = get_soup_from_url(self._url)
        return self._soup

    def data(self):
        if self._data is not None: return self._data

        soup = self.soup()
        if soup is None: return None
        s_type = soup.select('meta[property="og:type"]')[0].get('content')
        s_url = soup.select('meta[itemprop="url"]')[0].get('content')
        s_name = soup.select('meta[itemprop="name"]')[0].get('content')
        s_image = soup.select('meta[itemprop="image"]')[0].get('content')
        s_video_class = soup.select('meta[itemprop="class"]')[0].get('content')
        s_actor = soup.select('meta[itemprop="actor"]')[0].get('content')
        s_video = str(soup.select('meta[itemprop="video"]')[0].get('content'))
        s_video = s_video[s_video.index('http'): s_video.index('.mp4') + 4]
        s_duration = soup.select('meta[itemprop="duration"]')[0].get('content')
        s_upload_date = soup.select('meta[itemprop="uploadDate"]')[0].get('content')
        s_content_location = soup.select('meta[itemprop="contentLocation"]')[0].get('content')
        s_description = soup.select('meta[itemprop="description"]')[0].get('content')

        self._data = {
            'show_id': self.show_id,
            'type': s_type,
            'url': s_url,
            'name': s_name,
            'image': s_image,
            'video_class': s_video_class,
            'actor': s_actor,
            'video': s_video,
            'duration': s_duration,
            'upload_date': s_upload_date,
            'content_location': s_content_location,
            'description': s_description,
        }

        return self._data

    def save(self, update=False):
        if Show.objects.filter(show_id=self.show_id).exists() and not update:
            print(datetime.now(), 'show exists, skip')
            return False

        data = self.data()
        if data is None:
            return False

        show, created = Show.objects.update_or_create(show_id=self.show_id, defaults=data)
        print(datetime.now(), ' created: ', created)
        return True

    def get_show_id_list(self):
        soup = self.soup()
        shows = soup.select('div.caption.title > h5 > a')
        shows = [s.get('href') for s in shows]
        shows = [re.findall(r'\b\d+\b', s)[-1] for s in shows]
        return [int(s) for s in shows]

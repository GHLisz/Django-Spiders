import unittest
from datetime import datetime
from spiders.utils import get_soup_from_url
from emoticon.models import Photo, Article


class WebPhoto:
    def __init__(self, old_id, article_old_id=None):
        self.old_id = old_id
        self._article_old_id = article_old_id
        self._url = 'photo/' + str(self.old_id)
        self._soup = None
        self._data = None

    def soup(self):
        if self._soup is not None:
            return self._soup

        self._soup = get_soup_from_url(self._url)
        return self._soup

    def data(self):
        if self._data is not None:
            return self._data

        soup = self.soup()
        if soup is None:
            return None

        _pic_soup = soup.select("div.col-xs-12.col-sm-6.artile_des > table > tbody > tr > td > img")[0]
        title = _pic_soup['alt']
        date = datetime.strptime(
            soup.select('span[class="glyphicon glyphicon-time"]')[0].get_text(),
            '%Y-%m-%d')
        old_url = _pic_soup['src']
        bk_url = _pic_soup['onerror'].replace("this.src='", "")[:-1]
        tags = []
        for tag in soup.select("div.pic-tips > a.tips"):
            tags.append(tag.get_text())

        self._data = {
            'old_id': self.old_id,
            'article': self._article_old_id,
            'title': title,
            'date': date,
            'old_url': old_url,
            'bk_url': bk_url,
            'tags': tags
        }
        print("tags: ", tags)
        return self._data

    def save(self, update=False):
        if Photo.objects.filter(old_id=self.old_id).exists():
            if not update:
                print('photo exists, skip')
                return False

        data = self.data()
        if data is None:
            return False

        if data['article']:
            article = Article.objects.get(old_id=data['article'])
            print('fk found', article)
            data['article'] = article

        photo, created = Photo.objects.update_or_create(old_id=self.old_id,
                                                        defaults=data)

        photo.save()
        photo = Photo.objects.get(old_id=self.old_id)
        photo.tags.add(*data['tags'])
        print('created:', created)
        return True


class WebArticleTestCase(unittest.TestCase):

    def setUp(self):
        self.web_photo = WebPhoto('8364925', article_old_id='1022586')
        # self.web_photo = WebPhoto('1052921')
        self.web_photo = WebPhoto('4381981')
        self.web_photo = WebPhoto('9443045')

    def test_data(self):
        print(self.web_photo.data())
        a = self.web_photo.save(update=True)
        print('save r:', a)


if __name__ == '__main__':
    unittest.main()

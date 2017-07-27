import unittest
from datetime import datetime
from spiders.utils import get_soup_from_url
from emoticon.models import Article


class WebArticle:
    def __init__(self, old_id):
        self.old_id = old_id
        self._url = 'article/detail/' + str(self.old_id)
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
        title = soup.select("h1 > a")[0].get_text()
        date = datetime.strptime(
            soup.select('span[class="glyphicon glyphicon-time"]')[0].get_text(),
            '%Y-%m-%d')
        author = soup.select('div[class="text-right"]')[0].get_text().replace('作者：', '')
        tags = []
        for tag in soup.select("div.pic-tips > a.tips"):
            tags.append(tag.get_text())

        self._data = {
            'old_id': self.old_id,
            'title': title,
            'date': date,
            'author': author,
            'tags': tags
        }
        print("tags: ", tags)
        return self._data

    def save(self, update=False):
        if Article.objects.filter(old_id=self.old_id).exists():
            if not update:
                print('article exists, skip')
                return False

        data = self.data()
        article, created = Article.objects.update_or_create(old_id=self.old_id,
                                                            defaults=data)
        article.save()
        article = Article.objects.get(old_id=self.old_id)
        article.tags.add(*data['tags'])
        print('created:', created)
        return True

    def photo_ids(self):
        soup = self.soup()
        photo_ids = []
        for i in soup.select('div.artile_des > table > tbody > tr > td > a'):
            photo_id = i['href'].split('/')[-1]
            print('found photo id: ', photo_id)
            try:
                int(photo_id)  # article 4344065, 2596033 contains invalid photo
                photo_ids.append(photo_id)
            except (ValueError, TypeError):
                continue
        return photo_ids


class WebArticleTestCase(unittest.TestCase):

    def setUp(self):
        self.web_article = WebArticle('1022586')

    def test_data(self):
        print(self.web_article.data())
        a = self.web_article.save(update=True)
        print('save r:', a)

    def test_photo_ids(self):
        web_article = WebArticle('4338516')
        r = ['6181606', '1928032', '2051990', '6731772', '9798823', '3081699', '3689467', '4657860', '4972172']
        self.assertEqual(web_article.photo_ids(), r)
        web_article = WebArticle('4871399')
        r = ['7051824', '9472002', '4618174', '7560060', '5549929', '1031759', '7685282', '9058259', '9725533']
        self.assertEqual(web_article.photo_ids(), r)


if __name__ == '__main__':
    unittest.main()

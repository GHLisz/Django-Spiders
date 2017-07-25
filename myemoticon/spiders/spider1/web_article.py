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

        self._data = {
            'old_id': self.old_id,
            'title': title,
            'date': date,
            'author': author,
        }
        return self._data

    def save(self, update=False):
        article = Article(old_id=self.old_id)
        if (article is not None) and (not update):
            return False

        article, created = Article.objects.update_or_create(**self._data)
        article.save()
        print('created:', created)
        return True


class WebArticleTestCase(unittest.TestCase):

    def setUp(self):
        self.web_article = WebArticle('7541562')

    def test_data(self):
        print(self.web_article.data())
        a = self.web_article.save()
        print('save r:', a)


if __name__ == '__main__':
    unittest.main()

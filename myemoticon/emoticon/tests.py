from django.test import TestCase
from .models import Article, Photo
from datetime import datetime


# Create your tests here.
class ArticleTestCase(TestCase):
    def setUp(self):
        article = Article.objects.create(old_id=1,
                                         title='test',
                                         date=datetime.now(),
                                         author='a')
        articl2 = Article.objects.create(old_id=2,
                                         title='test',
                                         date=datetime.now(),
                                         author='a')
        for i in range(2):
            Photo.objects.create(old_id=i,
                                 article=article,
                                 title=str(i),
                                 date=datetime.now(),
                                 old_url='http://old'+str(i),
                                 bk_url='//aaa.com/production/uploads/image/2015/12/07/201.jpg'+str(i),
                                 cached=False)
        for i in range(2, 5):
            Photo.objects.create(old_id=i,
                                 article=article,
                                 title=str(i),
                                 date=datetime.now(),
                                 old_url='http://old'+str(i),
                                 bk_url='http://aaa.com/production/uploads/image/2015/12/07/201.jpg'+str(i),
                                 cached=False)

    def test_first_4_photo(self):
        article = Article.objects.get(old_id=1)
        first_4_photo = article.first_4_photo
        r = ['/production/uploads/image/2015/12/07/201.jpg0',
             '/production/uploads/image/2015/12/07/201.jpg1',
             '/production/uploads/image/2015/12/07/201.jpg2',
             '/production/uploads/image/2015/12/07/201.jpg3']
        self.assertEqual(first_4_photo, r)

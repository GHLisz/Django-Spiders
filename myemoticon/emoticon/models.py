from django.db import models
from taggit.managers import TaggableManager


# Create your models here.
class Article(models.Model):
    old_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=256)
    date = models.DateField()
    author = models.CharField(max_length=256)

    tags = TaggableManager()

    @property
    def first_4_photo(self):
        val = []
        photos = Photo.objects.filter(article=self)
        bk_urls = [i.bk_url for i in photos[:4]]
        for bk_url in bk_urls:
            bk_full_url = bk_url if bk_url.startswith('http:') else 'http:' + bk_url
            pic_partial_path = '/' + '/'.join(bk_full_url.replace('http://', '').split('/')[1:])
            val.append(pic_partial_path)
        return val

    def __str__(self):
        return 'Article id: {}, title: {}'.format(self.old_id, self.title)


class Photo(models.Model):
    old_id = models.IntegerField(unique=True)
    article = models.ForeignKey(Article, blank=True, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=256)
    date = models.DateField()
    old_url = models.URLField()
    bk_url = models.URLField()
    cached = models.BooleanField(default=False)

    tags = TaggableManager()

    def __str__(self):
        return 'Photo id: {}, title: {}'.format(self.old_id, self.title)

    @property
    def url(self):
        bk_full_url = self.bk_url if self.bk_url.startswith('http:') else 'http:' + self.bk_url
        pic_partial_path = '/' + '/'.join(bk_full_url.replace('http://', '').split('/')[1:])
        return pic_partial_path

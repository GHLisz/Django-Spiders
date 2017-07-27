from django.db import models
from taggit.managers import TaggableManager


# Create your models here.
class Article(models.Model):
    old_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=256)
    date = models.DateField()
    author = models.CharField(max_length=256)

    tags = TaggableManager()

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

from datetime import datetime

from django.conf import settings
from django.db import models


# Create your models here.
class Show(models.Model):
    show_id = models.BigIntegerField()
    type = models.CharField(max_length=1023, blank=True)
    url = models.URLField()
    name = models.CharField(max_length=1023, blank=True)
    image = models.URLField()
    video_class = models.CharField(max_length=1023, blank=True)
    actor = models.CharField(max_length=1023, blank=True)
    video = models.URLField()
    duration = models.CharField(max_length=255, blank=True)
    upload_date = models.CharField(max_length=255, blank=True)
    content_location = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=1023, blank=True)

    image_cached = models.BooleanField(default=False)
    image_update_time = models.DateTimeField(default=datetime(2000, 1, 1), verbose_name='image down job update time')
    video_cached = models.BooleanField(default=False)
    video_update_time = models.DateTimeField(default=datetime(2000, 1, 1), verbose_name='video down job update time')

    add_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Show(url="{self.url}", name="{self.name}", video="{self.video}")'

    @property
    def actor_safe(self):
        return self.actor if self.actor else 'NULL'

    @property
    def video_basesname(self):
        return self.video.split('//')[-1].split('/')[-1]

    @property
    def video_cdn_url(self):
        video = self.video_basesname
        return settings.VIDEO_CDN + video

    @property
    def video_cache_url(self):
        video = self.video_basesname
        return settings.VIDEO_CACHE_HTTP + '/'.join(list(video[:2].lower())) + '/' + video

    @property
    def video_cache_path(self):
        video = self.video_basesname
        return settings.VIDEO_CACHE + '\\'.join(list(video[:2].lower())) + '\\' + video

    @property
    def image_basename(self):
        return self.image.split('//')[-1].split('/')[-1]

    @property
    def image_cdn_url(self):
        image = self.image_basename
        return settings.IMAGE_CDN + image

    @property
    def image_cache_url(self):
        image = self.image_basename
        return settings.IMAGE_CACHE_HTTP + '/'.join(list(image[:2].lower())) + '/' + image

    @property
    def image_cache_path(self):
        image = self.image_basename
        return settings.IMAGE_CACHE + '\\'.join(list(image[:2].lower())) + '\\' + image

    @classmethod
    def get_object_from_any_video(cls, video_str):
        basename = video_str.replace('\\', '/').split('/')[-1]
        return cls.objects.filter(video__icontains=basename)

    @classmethod
    def get_object_from_any_image(cls, image_str):
        basename = image_str.replace('\\', '/').split('/')[-1]
        return cls.objects.filter(image__icontains=basename)

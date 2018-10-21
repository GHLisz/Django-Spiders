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
    def video_cache_url(self):
        old_video_path = self.video.split('//')[-1].split('/')[-1]
        new_video_url = settings.VIDEO_CACHE_HTTP + '/'.join(list(old_video_path[:2].lower())) + '/' + old_video_path
        return new_video_url

    @property
    def image_cache_url(self):
        old_image_path = self.image.split('//')[-1].split('/')[-1]
        new_image_url = settings.IMAGE_CACHE_HTTP + '/'.join(list(old_image_path[:2].lower())) + '/' + old_image_path
        return new_image_url

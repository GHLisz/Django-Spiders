from django.db import models
from datetime import datetime


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

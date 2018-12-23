import random
from datetime import datetime, timedelta

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
        return self.actor.replace('/', '_') if self.actor else 'NULL'

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

    @classmethod
    def get_down_video_job(cls):
        bulk_size = 20
        time_threshold = datetime.now() - timedelta(days=2)
        shows_to_down = cls.objects.filter(video_cached=False,
                                           video_update_time__lt=time_threshold).all()
        shows_to_down = list(shows_to_down)
        if len(shows_to_down) > bulk_size:
            shows_to_down = random.sample(shows_to_down, bulk_size)

        print(*shows_to_down, sep='\n')

        payload = []
        for s in shows_to_down:
            payload.append({'src': s.video_cdn_url, 'dst': s.video_cache_path})
            s.video_update_time = datetime.now()
            s.save()
        return payload

    @classmethod
    def process_down_video_result(cls, failed_jobs, passed_jobs):
        for video in failed_jobs:
            for s in cls.get_object_from_any_video(video):
                print('failed', s)
                s.video_update_time = datetime(2000, 1, 1)
                s.video_cached = False
                s.save()

        for video in passed_jobs:
            for s in cls.get_object_from_any_video(video):
                print('passed', s)
                s.video_cached = True
                s.save()

    @classmethod
    def get_down_image_job(cls):
        bulk_size = 20
        time_threshold = datetime.now() - timedelta(days=2)
        shows_to_down = cls.objects.filter(image_cached=False,
                                           image_update_time__lt=time_threshold).all()
        shows_to_down = list(shows_to_down)
        if len(shows_to_down) > bulk_size:
            shows_to_down = random.sample(shows_to_down, bulk_size)

        print(*shows_to_down, sep='\n')

        payload = []
        for s in shows_to_down:
            payload.append({'src': s.image_cdn_url, 'dst': s.image_cache_path})
            s.image_update_time = datetime.now()
            s.save()
        return payload

    @classmethod
    def process_down_image_result(cls, failed_jobs, passed_jobs):
        for image in failed_jobs:
            for s in Show.get_object_from_any_image(image):
                print('failed', s)
                s.image_update_time = datetime(2000, 1, 1)
                s.image_cached = False
                s.save()

        for image in passed_jobs:
            for s in Show.get_object_from_any_image(image):
                print('passed', s)
                s.image_cached = True
                s.save()

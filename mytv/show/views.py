import datetime
import json
import random
from urllib.parse import urlparse
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Show
from django.conf import settings


# Create your views here.
def index(request):
    return render(request, 'index.html')


def search_name(request):
    keyword = request.GET.get('q', '')
    print('keyword is ', keyword)
    name_hits = Show.objects.filter(name__icontains=keyword)
    return render(request, 'show/search_results.html', {'name_hits': name_hits})


@csrf_exempt
def down_video_job(request):
    if request.method == 'GET':
        bulk_size = 20
        time_threshold = datetime.datetime.now() - datetime.timedelta(days=2)
        shows_to_down = Show.objects.filter(video_cached=False,
                                            video_update_time__lt=time_threshold).all()  # [:bulk_size]
        try:
            shows_to_down = random.sample(list(shows_to_down), bulk_size)  # avoid repeated down
        except ValueError:  # Sample larger than population or is negative
            print('here')
            return JsonResponse({'success': False})
        # if len(shows_to_down) < bulk_size: return JsonResponse({'success': False})

        print(*shows_to_down, sep='\n')

        payload = []
        for s in shows_to_down:
            old_src = s.video
            old_path = old_src.split('//')[-1].split('/')[-1]
            new_src = settings.VIDEO_CDN + old_path
            new_dst = settings.VIDEO_CACHE + '\\'.join(list(old_path[:2].lower())) + '\\' + old_path
            payload.append({'src': new_src, 'dst': new_dst})
            s.video_update_time = datetime.datetime.now()
            s.save()
        return JsonResponse({'success': True, 'jobs': payload})

    elif request.method == 'POST':
        data = json.loads(request.body)
        failed_jobs = data['failed_jobs']
        passed_jobs = data['passed_jobs']

        print(data)

        for video in failed_jobs:
            old_video = video.replace(settings.VIDEO_CDN, settings.VIDEO_CDN_ORIGINAL)
            for s in Show.objects.filter(video=old_video):
                print('failed', s)
                s.video_update_time = datetime.datetime(2000, 1, 1)
                s.video_cached = False
                s.save()

        for video in passed_jobs:
            old_video = video.replace(settings.VIDEO_CDN, settings.VIDEO_CDN_ORIGINAL)
            for s in Show.objects.filter(video=old_video):
                print('passed', s)
                s.video_cached = True
                s.save()

    return JsonResponse({'success': True})

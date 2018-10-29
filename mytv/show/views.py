import datetime
import json
import random

from django.conf import settings
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Show


# Create your views here.
def index(request):
    return render(request, 'index.html')


def single_show(request, show_id):
    show = get_object_or_404(Show, show_id=show_id)
    fields = [f.attname for f in Show._meta.get_fields()]
    details = [(f, getattr(show, f, None)) for f in fields]
    return render(request, 'show/single_show.html', {'show': show, 'details': details})


def single_actor(request, actor_name):
    if actor_name == 'NULL':
        shows = Show.objects.filter(actor='')
    else:
        shows = Show.objects.filter(actor__iexact=actor_name)
    return render(request, 'show/single_actor.html', {'shows': shows, 'actor': actor_name})


def show_list(request):
    res = Show.objects.all().order_by('-show_id')
    paginator = Paginator(res, 20)

    page = request.GET.get('page')
    shows = paginator.get_page(page)
    return render(request, 'show/show_list.html', {'shows': shows})


def search_name(request):
    keyword = request.GET.get('q', '')
    name_hits = Show.objects.filter(name__icontains=keyword)
    return render(request, 'show/search_results.html', {'name_hits': name_hits})


@csrf_exempt
def down_video_job(request):
    if request.method == 'GET':
        bulk_size = 20
        time_threshold = datetime.datetime.now() - datetime.timedelta(days=2)
        shows_to_down = Show.objects.filter(video_cached=False,
                                            video_update_time__lt=time_threshold).all()
        try:
            shows_to_down = random.sample(list(shows_to_down), bulk_size)  # avoid repeated down
        except ValueError:  # Sample larger than population or is negative
            print('well, there are little to down')
            return JsonResponse({'success': False})

        print(*shows_to_down, sep='\n')

        payload = []
        for s in shows_to_down:
            payload.append({'src': s.video_cdn_url, 'dst': s.video_cache_path})
            s.video_update_time = datetime.datetime.now()
            s.save()
        return JsonResponse({'success': True, 'jobs': payload})

    elif request.method == 'POST':
        data = json.loads(request.body)
        failed_jobs = data['failed_jobs']
        passed_jobs = data['passed_jobs']

        print(data)

        for video in failed_jobs:
            for s in Show.get_object_from_any_video(video):
                print('failed', s)
                s.video_update_time = datetime.datetime(2000, 1, 1)
                s.video_cached = False
                s.save()

        for video in passed_jobs:
            for s in Show.get_object_from_any_video(video):
                print('passed', s)
                s.video_cached = True
                s.save()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False})


@csrf_exempt
def down_image_job(request):
    if request.method == 'GET':
        bulk_size = 20
        time_threshold = datetime.datetime.now() - datetime.timedelta(days=2)
        shows_to_down = Show.objects.filter(image_cached=False,
                                            image_update_time__lt=time_threshold).all()  # [:bulk_size]
        try:
            shows_to_down = random.sample(list(shows_to_down), bulk_size)  # avoid repeated down
        except ValueError:  # Sample larger than population or is negative
            print('well, there are little to down')
            return JsonResponse({'success': False})

        print(*shows_to_down, sep='\n')

        payload = []
        for s in shows_to_down:
            payload.append({'src': s.image_cdn_url, 'dst': s.image_cache_path})
            s.image_update_time = datetime.datetime.now()
            s.save()
        return JsonResponse({'success': True, 'jobs': payload})

    elif request.method == 'POST':
        data = json.loads(request.body)
        failed_jobs = data['failed_jobs']
        passed_jobs = data['passed_jobs']

        print(data)

        for image in failed_jobs:
            for s in Show.get_object_from_any_image(image):
                print('failed', s)
                s.image_update_time = datetime.datetime(2000, 1, 1)
                s.image_cached = False
                s.save()

        for image in passed_jobs:
            for s in Show.get_object_from_any_image(image):
                print('passed', s)
                s.image_cached = True
                s.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})

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
        payload = Show.get_down_video_job()
        if not payload:
            print('well, there are noting to down')
            return JsonResponse({'success': False})
        return JsonResponse({'success': True, 'jobs': payload})

    elif request.method == 'POST':
        data = json.loads(request.body)
        print(data)

        failed_jobs = data['failed_jobs']
        passed_jobs = data['passed_jobs']

        Show.process_down_video_result(failed_jobs, passed_jobs)
        return JsonResponse({'success': True, 'pass_count': len(passed_jobs)})

    return JsonResponse({'success': False})


@csrf_exempt
def down_image_job(request):
    if request.method == 'GET':
        payload = Show.get_down_image_job()
        if not payload:
            print('well, there are noting to down')
            return JsonResponse({'success': False})
        return JsonResponse({'success': True, 'jobs': payload})

    elif request.method == 'POST':
        data = json.loads(request.body)
        print(data)

        failed_jobs = data['failed_jobs']
        passed_jobs = data['passed_jobs']

        Show.process_down_image_result(failed_jobs, passed_jobs)
        return JsonResponse({'success': True, 'pass_count': len(passed_jobs)})

    return JsonResponse({'success': False})

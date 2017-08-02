from django.shortcuts import render
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Article, Photo


# Create your views here.
class ArticleListView(ListView):
    queryset = Article.objects.all()
    context_object_name = 'articles'
    paginate_by = 10
    template_name = 'emoticon/article_list.html'


class StandalonePhotoListView(ListView):
    queryset = Photo.objects.filter(article_id__isnull=True)
    context_object_name = 'standalone_photos'
    paginate_by = 50
    template_name = ''


def article_list(request):
    object_list = Article.objects.all()
    paginator = Paginator(object_list, 10)
    page = request.GET.get('page')

    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    return render(request, 'emoticon/article_list.html', {
        'articles': articles,
    })

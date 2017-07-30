from django.shortcuts import render
from django.views.generic import ListView
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

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Article, Photo
from taggit.managers import TaggableManager


# Create your views here.
class ArticleListView(ListView):
    queryset = Article.objects.all().order_by('-date')
    context_object_name = 'articles'
    paginate_by = 10
    template_name = 'emoticon/article_list.html'


class StandalonePhotoListView(ListView):
    queryset = Photo.objects.filter(article_id__isnull=True).order_by('-date')
    context_object_name = 'standalone_photos'
    paginate_by = 48
    template_name = 'emoticon/standalone_photo_list.html'


class TagListView(ListView):
    context_object_name = 'standalone_photos'
    paginate_by = 48
    template_name = 'emoticon/standalone_photo_list.html'

    def get_queryset(self):
        return Photo.objects.filter(tags__slug=self.kwargs['tag_slug'])


def article_detail(request, article_old_id):
    article = get_object_or_404(Article, old_id=article_old_id)
    photos = Photo.objects.filter(article=article)

    tags = article.tags.all()

    return render(request, 'emoticon/article_detail.html', {'article': article,
                                                            'photos': photos,
                                                            'tags': tags})


def photo_detail(request, photo_old_id):
    photo = get_object_or_404(Photo, old_id=photo_old_id)
    tags = photo.tags.all()

    photo_tags_ids = photo.tags.values_list('id', flat=True)
    similar_photos = Photo.objects.filter(tags__in=photo_tags_ids).exclude(id=photo.id)
    similar_photos = similar_photos.annotate(same_tags=Count('tags')).order_by('-same_tags', '-date')[:8]

    return render(request, 'emoticon/photo_detail.html', {'photo': photo,
                                                          'tags': tags,
                                                          'similar_photos': similar_photos})

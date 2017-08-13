from django.conf.urls import url
from django.views.generic import RedirectView
from . import views


urlpatterns = [
    url(r'^article_list$', views.ArticleListView.as_view(), name='article_list'),
    url(r'^photo_list$', views.StandalonePhotoListView.as_view(), name='photo_list'),
    url(r'^article/(?P<article_old_id>\d+)/$', views.article_detail, name='article_detail'),
    url(r'^tag/(?P<tag_slug>[-\w]+)/$', views.TagListView.as_view(), name='tag_list'),
    url(r'^photo/(?P<photo_old_id>\d+)/$', views.photo_detail, name='photo_detail'),
    url(r'^$', RedirectView.as_view(url='article_list')),
]

from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.ArticleListView.as_view(), name='article_list'),
]
"""mytv URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from show import views as show_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/down_video_job/', show_views.down_video_job, name='down_video_job'),
    path('api/down_image_job/', show_views.down_image_job, name='down_image_job'),
    path('show/<int:show_id>', show_views.single_show, name='single_show'),
    path('actor/<str:actor_name>', show_views.single_actor, name='single_actor'),
    path('list/', show_views.show_list, name='show_list'),
    path('search/', show_views.search_name, name='search_name'),
    path('', show_views.index, name='index'),
]

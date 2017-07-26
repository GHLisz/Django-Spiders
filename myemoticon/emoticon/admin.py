from django.contrib import admin
from .models import Article, Photo


# Register your models here.
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'old_id', 'title', 'date', 'author',)
    search_fields = ('title', )
    ordering = ['date', 'old_id']
    date_hierarchy = 'date'


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'old_id', 'title', 'date', 'old_url', 'bk_url', 'cached')
    search_fields = ('title', )
    ordering = ['date', 'old_id']
    date_hierarchy = 'date'

admin.site.register(Article, ArticleAdmin)
admin.site.register(Photo, PhotoAdmin)

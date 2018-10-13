from django.contrib import admin
from .models import Show


# Register your models here.
class ShowAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Show._meta.get_fields()]
    search_fields = ['name', 'actor']


admin.site.register(Show, ShowAdmin)

from django.contrib import admin
from .models import *

class ItemAdmin(admin.ModelAdmin):
    list_display=['name','price','category']
    list_filter=['category','location']
    search_fields=['name','price','category','description']
# Register your models here.

admin.site.register(Item)
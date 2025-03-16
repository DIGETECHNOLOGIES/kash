from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Shop)
admin.site.register(Account)
admin.site.register(Image)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Order)
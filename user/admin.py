from django.contrib import admin
from .models import User, Location, Gain


# Register your models here.
admin.site.register(User)
admin.site.register(Location)
admin.site.register(Gain)

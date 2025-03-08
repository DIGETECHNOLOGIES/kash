from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.
class Location(models.Model):
    region = models.CharField(max_length=200)
    town = models.CharField(max_length=200, null = True)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable=False)
    email = models.EmailField(null=False, unique=True)
    image = models.ImageField(upload_to='profiles')
    number = models.CharField(max_length=20, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    # location = models.CharField(max_length=200, null=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def  __str__(self):
        return self.username
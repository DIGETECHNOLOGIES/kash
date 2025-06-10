from django.db import models
from shop.models import User, Shop

# Create your models here.
class Message(models.Model):
    sender_type = models.CharField(max_length=20, default='user')
    sender_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="send", null=True)
    sender_shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="send", null=True)

    receiver_shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="receive", null=True)
    receiver_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receive", null=True)

    text = models.TextField()
    image = models.ImageField(upload_to='messages/images')
    video = models.FileField(upload_to='messages/videos')

    created = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['created']
    


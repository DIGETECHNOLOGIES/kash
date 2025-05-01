from django.db import models
from user.models import User, Location
import math

# Create your models here.

def Id_card_directory(instance, filename):
    return f'IDcards/{instance.owner.username}/{filename}'


class Shop(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=200)
    image= models.ImageField(upload_to='shop/', null=True)
    location = models.ForeignKey(Location, related_name="shop_location", on_delete=models.SET_NULL, null=True)
    workers = models.ManyToManyField(User, related_name="shop_workers")
    owner_image = models.ImageField(upload_to='shop_owners/', null=True)
    front_IDCard = models.ImageField(upload_to=Id_card_directory, null=True)
    back_IDCard = models.ImageField(upload_to=Id_card_directory, null=True)
    is_verified = models.BooleanField(default=False)


    def __str__(self):
        return self.name
    
class Account(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    available_balance = models.PositiveIntegerField(default=0)
    pending_balance = models.PositiveIntegerField(default=0)


    def __str__(self):
        return self.shop.name

class Category(models.Model):
    CATEGORY_CHOICE=[('electronics', 'Electronics'),
        ('fashion', 'Fashion'),
        ('home', 'Home & Kitchen'),
        ('books', 'Books'),
        ('other', 'Other'),]

    name = models.CharField(max_length=255,choices=CATEGORY_CHOICE,default='other')

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
class Image(models.Model):
    image = models.ImageField(upload_to='products/')
    created = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created']

class Item(models.Model):
    name = models.CharField(max_length=200)
    shop = models.ForeignKey(Shop, null=True, on_delete=models.SET_NULL)
    description = models.TextField(null = True)
    images = models.ManyToManyField(Image)
    location = models.ForeignKey(Location,  on_delete=models.CASCADE,null=True,blank=True)
    previous_price = models.PositiveIntegerField(null=True)
    current_price = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created']
    
    
    def __str__(self):
        return self.name
    

class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    total = models.PositiveIntegerField(default=0)
    delivered = models.BooleanField(default=False)
    number = models.CharField(default="0", max_length=9)
    payment_id = models.CharField(max_length=20, default='1111111111')
    payment_status = models.CharField(default='Pending', max_length=20)
    created = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created']


    def __str__(self):
        return self.item.name
    
    def save(self, *args, **kwargs):
        self.total = self.quantity * self.item.current_price
        super().save(*args, **kwargs)


class Withdrawal(models.Model):
    shop = models.ForeignKey(Shop, related_name='withdraw', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    amount_to_receive = models.PositiveIntegerField()
    charges = models.CharField(max_length=20, default=f'0')
    number = models.CharField(max_length= 20)
    service = models.CharField(max_length=20, default="MTN")
    status = models.CharField(max_length=20, default="Pending")
    created = models.DateTimeField(auto_now_add=True)
    # created = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created']

    REQUIRED_FIELDS = []
    # name = models.PositiveIntegerField()


    def __str__(self):
        return f'{self.shop.name}:{self.id}'
    
    def save(self, *args, **kwargs):
        self.amount_to_receive = self.amount*0.94
        self.charges = self.amount*0.06
        super().save(*args, **kwargs)
    


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    choices = [
        ('Pending', 'PENDING'),
        ('Rejected', 'REJECTED'),
        ('Paid', 'PAID')
    ]
    status = models.CharField(max_length=20, choices=choices)
    reason = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    amount = models.PositiveIntegerField(default=1)


    class Meta:
        ordering = ['-created']

    def save(self, *args, **kwargs):
        self.amount = math.floor(self.order.total * 0.96)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.order.buyer.username}: {self.order.item.name} - {self.order.total * 0.95}'
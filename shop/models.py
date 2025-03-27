from django.db import models
from user.models import User, Location

# Create your models here.
class Shop(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=200)
    image= models.ImageField(upload_to='shop/', null=True)
    location = models.ForeignKey(Location, related_name="shop_location", on_delete=models.SET_NULL, null=True)
    workers = models.ManyToManyField(User, related_name="shop_workers")
    owner_image = models.ImageField(upload_to='shop_owners/', null=True)
    IDCard = models.ImageField(upload_to='IDcards/', null=True)
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


    def __str__(self):
        return self.item.name
    
    def save(self, *args, **kwargs):
        self.total = self.quantity * self.item.current_price
        super().save(*args, **kwargs)


class Withdrawal(models.Model):
    shop = models.ForeignKey(Shop, related_name='withdraw', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    number = models.CharField(max_length= 20)
    service = models.CharField(max_length=20, default="MTN")
    status = models.CharField(max_length=20, default="Pending")


    def __str__(self):
        return f'{self.shop.name}:{self.id}'
    


# class Refund(models.Model):
    # order = models.
from .models import Item
from rest_framework import serializers

class PriceValidator:
     def __call__(self,value):
        if value<=0:
            raise serializers.ValidationError("Price must be a positive number")
        return value

class ItemSerializer(serializers.ModelSerializer):
    CATEGORY_CHOICE=[('electronics', 'Electronics'),
        ('fashion', 'Fashion'),
        ('home', 'Home & Kitchen'),
        ('books', 'Books'),
        ('other', 'Other'),]
    name=serializers.CharField(max_length=255,)
    description=serializers.CharField(max_length=255,)
    location=serializers.CharField(max_length=255,)
    category=serializers.ChoiceField(choices=CATEGORY_CHOICE,default='other')
    price=serializers.DecimalField(max_digits=10,decimal_places=0,validators=[PriceValidator()])
    image=serializers.ImageField(required=False)
    class Meta:
        model=Item
        fields=['name','price','description','location','category','image']
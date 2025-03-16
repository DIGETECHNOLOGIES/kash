from .models import Item
from shop.models import Category,Location,Image
from rest_framework import serializers

class PriceValidator:
     def __call__(self,value):
        if value<=0:
            raise serializers.ValidationError("Price must be a positive number")
        return value

class ItemSerializer(serializers.ModelSerializer):
    id=serializers.IntegerField(read_only=True)
    name=serializers.CharField(max_length=255,)
    description=serializers.CharField(max_length=255,)
    location=serializers.StringRelatedField(required=False,allow_null=True)
    category=serializers.StringRelatedField()
    current_price=serializers.DecimalField(max_digits=10,decimal_places=0,validators=[PriceValidator()])
    images=serializers.ImageField()
    class Meta:
        model=Item
        fields=['id','name','current_price','description','location','category','images']
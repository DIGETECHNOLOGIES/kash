from .models import Item
from shop.models import Category,Location,Image
from rest_framework import serializers
from django.core.exceptions import ValidationError
# from shop.serializers import ImageSerializer

class PriceValidator:
    def __call__(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive number")
        return value

def validate_image_size(image):
    max_size = 2 * 1024 * 1024  # 2MB
    if image.size > max_size:
        raise serializers.ValidationError("Each image size must not exceed 2MB")
    return image


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Image  
        fields = ['url']

    def get_url(self, obj):
        request = self.context.get('request') 
        if obj.image.url and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=255)
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    current_price = serializers.DecimalField(max_digits=10, decimal_places=0, validators=[PriceValidator()])
    images = ImageSerializer(many = True, required = False)

    class Meta:
        model = Item
        fields = ['id','name', 'current_price', 'description', 'location', 'category', 'images']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])  
        item = Item.objects.create(**validated_data)  

        for image_data in images_data:
            image = Image.objects.create(image=image_data)  
            item.images.add(image)  
        item.save()
        return item

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])  
        instance.name = validated_data.get('name', instance.name)
        instance.current_price = validated_data.get('current_price', instance.current_price)
        instance.description = validated_data.get('description', instance.description)
        instance.location = validated_data.get('location', instance.location)
        instance.category = validated_data.get('category', instance.category)
        instance.save()

        if images_data:
            instance.images.clear()  
            for image_data in images_data:
                image = Image.objects.create(image=image_data)
                instance.images.add(image)

        return instance

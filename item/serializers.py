from .models import Item
from shop.models import Category, Location, Image, Shop
from rest_framework import serializers

from shop.serializers import ShopSerializer

class PriceValidator:
    def __call__(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive number")
        return value

class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['url']

    def get_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class ItemSerializer(serializers.ModelSerializer):
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all() , required = False)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required = False)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=0, validators=[PriceValidator()])
    images = ImageSerializer(many=True, required = False)  
    shop = ShopSerializer(required = False)

    class Meta:
        model = Item
        fields = ['id', 'name', 'shop', 'current_price','previous_price', 'description', 'location', 'category', 'images']
        read_only_fields = ['id', 'shop']  # Make 'id' read-only

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        shop = Shop.objects.get(owner = user)
        images_data = validated_data.pop('images', [])
        item = Item.objects.create(**validated_data)
        item.shop = shop

        for image_data in images_data:
            image = Image.objects.create(image=image_data)
            item.images.add(image)  # Associate the image with the item

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

        # Handle image updates
        if images_data:
            instance.images.clear()  # Remove all previous images
            for image_data in images_data:
                image = Image.objects.create(image=image_data)
                instance.images.add(image)

        return instance



from rest_framework import serializers

def validate_image(image):
    max_size = 5 * 1024 * 1024
    if image.size > max_size:
        raise serializers.ValidationError({'message':'Image size is more than 5mb'})
    return image

def validate_quantity(quantity):
    if quantity < 1:
        raise serializers.ValidationError({'message':'Quantity cannot be less than 1'})
    return quantity
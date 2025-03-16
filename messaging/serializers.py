from rest_framework import serializers
from .models import Message, User, Shop

from shop.serializers import ShopSerializer


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    class Meta:
        model =User
        fields = [
            'id',
            'name',
            'email',
        ]
    
    def get_name(self, obj):
        return obj.username



class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    receiver = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'receiver',
            'created',
            # 'image',
            # 'video',
            'text',
            'sender_type',
        ]

    def get_sender(self,obj):
        if obj.sender_type == 'user':
            return UserSerializer(obj.sender_user).data
        return ShopSerializer(obj.sender_shop).data
    
    def get_receiver(self,obj):
        if obj.sender_type == 'user':
            return ShopSerializer(obj.receiver_shop).data
        return UserSerializer(obj.receiver_user).data
    
    def validate(self, data):
        view = self.context.get('view')
        user = User.objects.get(id = view.kwargs.get('user'))
        shop = Shop.objects.get(id=view.kwargs.get('shop'))
        if data['sender_type'] == 'user':
            # view.kwargs.get('sender')
            data['sender_user'] = user
            data['receiver_shop'] = shop
        else :
            data['sender_shop'] = shop
            data['receiver_user'] = user
        # data.pop('sender')
        # data.pop('receiver')
        return data
    
    def create(self, validated_data):
        message = Message.objects.create(**validated_data)
        return message
    
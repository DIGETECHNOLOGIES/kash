from rest_framework import serializers
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from .models import Shop, User, Location, Account, Item, Order
from .validators import validate_image, validate_quantity

def mail(name, user):
    subject = "Shop Verification Request"
    message = f'{user} requests to verify {name} as a shop'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient = from_email

    send_mail(
        subject=subject, 
        message=message, 
        from_email= recipient, 
        recipient_list= [recipient]
    )


class ShopCreationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only = True)
    location = serializers.PrimaryKeyRelatedField(queryset = Location.objects.all())
    owner_image = serializers.ImageField(validators =[validate_image] )
    IDCard = serializers.ImageField(validators =[validate_image])

    

    class Meta:
        model = Shop
        fields = [
            # 'owner',
            'name',
            'location',
            'owner_image',
            'IDCard',
        ]

    def create(self, data):
        request = self.context.get('request')
        user = request.user
        data['owner'] = request.user

        with transaction.atomic():
            shop = Shop.objects.create(**data)
            try:
                mail(user=user, name = data['name'])
                shop.save()
                account = Account(shop = shop)
                account.save()
            except Exception as e:
                raise serializers.ValidationError({'creation':'Error occured in creating shop. Please try again'})
        
        return shop

class OrderSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset = Item.objects.all())
    # buyer = serializers.PrimaryKeyRelatedField(queryset = User.objects.all())
    quantity = serializers.IntegerField(validators = [validate_quantity])

    class Meta:
        model = Order

        fields = [
            'item',
            'quantity',
        ]

    def create(self, data):
        request = self.context.get('request')
        buyer = request.user
        data['buyer'] = buyer

        with transaction.atomic():
            order = Order.objects.create(**data)
            subject = f'Order placed for {data["item"].name}'
            message = f'An order has been placed for {data["quantity"]} quantity of {data["item"].name}'
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    recipient_list=[data['item'].shop.owner.email], 
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    )
                order.save()

            except Exception as e:
                raise serializers.ValidationError({'Order':'Error placing order. Please try again'})
        
        return order

        


             





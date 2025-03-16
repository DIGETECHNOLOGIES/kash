from rest_framework import serializers
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from .models import Shop, User, Location, Account, Item, Order, Image
from .validators import validate_image, validate_quantity
from user.validators import validate_number
import uuid


#payment
from .payment import initiate_payment, confirm_payment


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

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Image  
        fields = ['id', 'url']

    def get_url(self, obj):
        request = self.context.get('request') 
        if obj.url and request:
            # return obj.url
            return request.build_absolute_uri(obj.url)
        return None





class ShopCreationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only = True)
    location = serializers.PrimaryKeyRelatedField(queryset = Location.objects.all())
    owner_image = serializers.ImageField(validators =[validate_image] )
    IDCard = serializers.ImageField(validators =[validate_image])

    

    class Meta:
        model = Shop
        fields = [
            'id',
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
    
class ShopSerializer(serializers.ModelSerializer):
    
    location = LocationSerializer(read_only = True)
    image = ImageSerializer()
    class Meta:
        model = Shop
        fields = [
            'id',
            'name',
            'location',
            'image'
        ]
    

class ItemSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only = True)
    location = LocationSerializer(read_only = True)
    images = ImageSerializer(many = True)

    class Meta:
        model = Item
        fields = [
            'id',
            'shop',
            'name',
            'images',
            'location'

        ]

class OrderSerializer(serializers.ModelSerializer):
    
    quantity = serializers.IntegerField(validators = [validate_quantity])
    number = serializers.CharField(validators = [validate_number])

    class Meta:
        model = Order

        fields = [
            'id',
            'item',
            'quantity',
            'number'
        ]

    def create(self, data):
        request = self.context.get('request')
        buyer = request.user
        data['buyer'] = buyer
        id = str(uuid.uuid4().hex[:10])

        with transaction.atomic():
            #payment logic here
            item = Item.objects.get(id = data['item'].id)
            order = Order.objects.create(**data)
            order.payment_id = id
            payment = initiate_payment(amount = order.total, id=id)
            if payment.status_code == 200:
                payment = confirm_payment(amount=order.total, id=id, number = order.number)
                if payment.status_code != 200:
                    raise serializers.ValidationError({'payment_failed':{payment.text}})
                else:
                    pass
            else:
                raise serializers.ValidationError({'payment_failed':{payment.text}})
            # print(data['item'])
            # account = Account.objects.get(shop = item.shop)
            # account.pending_balance += int(order.total)
            # account.save()
            # subject = f'Order placed for {data["item"].name}'
            # message = f'An order has been placed for {data["quantity"]} quantity of {data["item"].name}'
            # try:
            #     send_mail(
            #         subject=subject,
            #         message=message,
            #         recipient_list=[data['item'].shop.owner.email], 
            #         from_email=settings.DEFAULT_FROM_EMAIL,
            #         )
            #    

            # except Exception as e:
            #     raise serializers.ValidationError({'Order':'Error placing order. Please try again'})
            order.save()
        
        return order
    


# class PaymentConfirmserializer(serializers.Serializer):


class OrderViewSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only = True)

    class Meta:
        model = Order
        fields = [
            'id',
            'buyer',
            'item',
            'total',
            'quantity',
            'delivered'
        ]





class ItemViewSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only = True)
    location = LocationSerializer(read_only = True)


    class Meta:
        model = Item
        fields = '__all__'
        

             





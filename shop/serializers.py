from rest_framework import serializers
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from .models import Shop, User, Location, Account, Item, Order, Image, Withdrawal
from .validators import validate_image, validate_quantity
from user.validators import validate_number
from user.serializers import UserViewSerializer
import uuid
from .models import Refund

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
            return request.build_absolute_uri(obj.url)
        return None
    


class ImageSerializerForOrder(serializers.ModelSerializer):
    # url = serializers.SerializerMethodField()

    class Meta:
        model = Image  
        fields = ['id', 'url']

    # def get_url(self, obj):
    #     request = self.context.get('request') 
    #     if obj.url and request:
    #         return request.build_absolute_uri(obj.url)
    #     return None





class ShopCreationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only = True)
    location = serializers.PrimaryKeyRelatedField(queryset = Location.objects.all(), required = False)
    owner_image = serializers.ImageField(validators =[validate_image] )
    front_IDCard = serializers.ImageField(validators =[validate_image])
    back_IDCard = serializers.ImageField(validators =[validate_image])
    image = serializers.ImageField(validators =[validate_image])


    

    class Meta:
        model = Shop
        fields = [
            'id',
            'name',
            'location',
            'owner_image',
            'front_IDCard',
            'back_IDCard',
            'image',
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
                raise serializers.ValidationError({'message':'Error occured in creating shop. Please try again'})
        
        return shop
    
class ShopSerializer(serializers.ModelSerializer):
    
    location = LocationSerializer(read_only = True)
    # image = ImageSerializer()
    owner = UserViewSerializer()
    # owner = U
    class Meta:
        model = Shop
        fields = [
            'id',
            'name',
            'location',
            'image',
            'owner',
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
            'location',
            'description',
            'delivery'
        ]
    #Extract Incoming photos and change or maintain for Resale Fnctionality
    def create(self, validated_data):
        photos_data = validated_data.pop('photos', [])
        Item = Item.objects.create(**validated_data)
        for photo_data in photos_data:
            photo = Image.objects.create(**photo_data)
            Item.photos.add(photo)
        return Item

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
            import random
            code = str(random.randint(100000, 999999))
            order.code = str(order.id) + code
            payment = initiate_payment(amount = (int(order.total)*1.01), id=id)
            if payment.status_code == 200:
                payment = confirm_payment(amount=(int(order.total)*1.01), id=id, number = order.number)
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

class ItemViewSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only = True)
    location = LocationSerializer(read_only = True)


    class Meta:
        model = Item
        fields = '__all__'

class OrderViewSerializer(serializers.ModelSerializer):
    item = ItemViewSerializer(read_only = True)

    class Meta:
        model = Order
        fields = '__all__'





        


class WithdrawalRequestSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required = False)
    number = serializers.CharField(validators = [validate_number])
    class Meta:

        model = Withdrawal
        fields = ['id', 'number', 'amount', 'status', 'created','amount_to_receive', 'name']
        read_only_fields = ['id', 'created', 'amount_to_receive','status', 'name']

    def create(self, validated_data):
        id = self.context.get('id')
        request =  self.context.get('request')
        shop = Shop.objects.get(id = id)
        if request.user.id != shop.owner.id:
            serializers.ValidationError({'error':'Cannot place withdrawal for this shop'})
        validated_data['shop'] = shop
        validated_data['status'] = 'Pending'
        account = Account.objects.get(shop__id = id)
        amount = validated_data.get('amount')
        if int(amount) <= int(account.available_balance) and int(amount) >= 1000:
            withdrawal = Withdrawal.objects.create(**validated_data)
            account.available_balance -= int(amount)
            account.save()
            send_mail(
                message=f'A withdrawal request has been made by {account.shop}',
                subject='KASH withdrawal',
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                from_email=settings.DEFAULT_FROM_EMAIL

            )
            return withdrawal
        elif int(amount) < 1000:
            raise serializers.ValidationError({'message':'Amount is less than minimum withdrawal of 1000frs'})
        else:
            raise serializers.ValidationError({'message':'Amount is more than available balance'})

class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['id', 'order', 'reason', 'refund_amount', 'payment_method', 'evidense', 'status', 'submited_at', 'account_number', 'account_name']
        read_only_fields = ['status', 'submited_at']

    def validate_order(self, value):
        request = self.context['request']
        user = request.user
        # to ensure the order belongs to the user and is paid
        if value.buyer != user:
            raise serializers.ValidationError({"error":"This order does not belong to you."})
        if  value.payment_status != 'SUCCESSFUL':
            raise serializers.ValidationError({"error":"Cannot request a refund for an unpaid order."})
        if Refund.objects.filter(user=user, order=value).exists():
            raise serializers.ValidationError({"error":"Refund request already submitted for this order."})
        if value.payment_status != 'SUCCESSFUL':
            raise serializers.ValidationError({"error":"Cannot request a refund for an unpaid order."})
        return value

    def create(self, validated_data):
        
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'





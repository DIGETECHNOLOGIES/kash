from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, viewsets
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings

#serializers
from .serializers import ShopCreationSerializer, OrderSerializer, OrderViewSerializer, ItemViewSerializer, ShopSerializer
from .models import Order, Item, Account, Shop

# Create your views here.
class VerifyShop(generics.CreateAPIView):
    serializer_class = ShopCreationSerializer
    # permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()

        return Response({
            'success':'Shop Creation request submitted successfully, Our team is viewing your request and you will get a response in the next 5 business days. ',
           
        },  status=status.HTTP_201_CREATED)
    

class PlaceOrder(generics.CreateAPIView):
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response({
            'success':'Order placed successfully. Proceed to do payments'
        },  status=status.HTTP_201_CREATED)


class PaymentConfirmation(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # with transaction.atomic():
        try:
            data = request.data
            print(data)

            transaction_id = data.get('data', {}).get('transaction_id')
            status = data.get('data', {}).get('transaction_status')
            amount = data.get('data', {}).get('transaction_amount')
            currency = data.get('data', {}).get('transaction_currency')
            message = data.get('data', {}).get('message')
            order = Order.objects.get(payment_id = transaction_id)
            order.payment_status = status
            order.save()
            print('order is ',order.item.shop.owner.email)
            
            if status == 'SUCCESS':
                account = Account.objects.get(shop__id = order.item.shop.id)
                account.pending_balance += int(order.total)
                account.save()
                print('account is ',account)
                subject = f'Order placed for {order.item}'
                message = f'An order has been placed for {order.quantity} quantity of {order.item.name}'
                # try:
                send_mail(
                    subject=subject,
                    message=message,
                    recipient_list=[order.item.shop.owner.email], 
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    )
                return Response({"message": "Transaction updated successfully"}, status=200)
                    
                    

                # except Exception as e:
                #     # raise serializers.ValidationError({'Order':'Error placing order. Please try again'})
                #     return Response(
                #         {'error':f'Error sending mail: {e}'}
                #     )
        except Exception as e:
            return Response({
                'error':f'Internal server error'
            })




class BuyOrderView(generics.ListAPIView):
    serializer_class = OrderViewSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.filter(buyer = user)
        return qs
    

class SellOrderView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderViewSerializer
    # lookup_field = 'item.shop'

    def get_queryset(self):
        shop_id = self.kwargs['shop_id']
        qs = Order.objects.filter(item_id = shop_id)
        return qs


class ConfirmDelivery(generics.RetrieveUpdateAPIView):

    def get_object(self):
        user = self.request.user
        order_id = self.kwargs['order_id']
        try:

         return Order.objects.get(buyer = user, id = order_id)
        except:
            return None


    def update(self, request, *args, **kwargs):
        order = self.get_object()
        
        if order:
            order.delivered = True
            order.save()
            account = Account.objects.get(shop = order.item.shop)
            account.pending_balance -= order.total
            account.available_balance += order.total
            account.save()

            return Response(
                {
                    'success':'Item delivered successfully',
                }
            )
        return Response(
                {
                    'failed':'Order not found',
                    
                }
            )
    
class ViewItems(generics.ListAPIView):
    serializer_class = ItemViewSerializer
    queryset = Item.objects.all()

    def get_queryset(self):

        qs= Item.objects.filter(shop__is_verified = True)
        return qs


class SearchItems(viewsets.ModelViewSet):
    serializer_class = ItemViewSerializer
    filter_backends = (SearchFilter,)
    search_fields = ['name', 'category__name', 'sub_category__name']

    def get_queryset(self):
        
        return Item.objects.filter(shop__is_verified=False)


class ShopView(generics.RetrieveAPIView):
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()
    lookup_field = 'id'

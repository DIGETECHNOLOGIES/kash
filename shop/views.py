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
from .models import Refund

from rest_framework.permissions import IsAuthenticated 
#serializers
from .serializers import ShopCreationSerializer, OrderSerializer, OrderViewSerializer, ItemViewSerializer, ShopSerializer, WithdrawalRequestSerializer
from item.serializers import ItemSerializer
from .models import Order, Item, Account, Shop, Withdrawal
from .serializers import RefundSerializer

from .payment import verify_payment

import random
import string

def generate_code(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))

# code = generate_code()
# print(code)

# Create your views here.
class VerifyShop(generics.CreateAPIView):
    serializer_class = ShopCreationSerializer
    # permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()

        return Response({
            'success':'Shop Creation request submitted successfully, Our team is viewing your request and you will get a response in at most 5 business days. ',
           
        },  status=status.HTTP_201_CREATED)
    

class PlaceOrder(generics.CreateAPIView):
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response({
            'success':'Order placed successfully. To confirm order Dial *126# and confirm payment from your MoMo. Additional charges may apply.'
        },  status=status.HTTP_201_CREATED)


class PaymentConfirmation(APIView):
    # permission_classes = [AllowAny]

    def get(self, request, id):
        
            data = verify_payment(id = id)
            data = data.get('data')
            transaction_id = data.get('transaction_id')
            status = data.get("transaction_status", "UNKNOWN")
            print('status', status)
            message = data.get('message')
            order = Order.objects.get(payment_id = transaction_id)
            order.payment_status = status
            order.code = generate_code()

            order.save()
            print('order is ',order.item.shop.owner.email)
            
            if status == 'SUCCESS':
                account = Account.objects.get(shop__id = order.item.shop.id)
                account.pending_balance += int(order.total)
                account.save()
                print('here')
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
                return Response({"Success": "Payment completed"}, status=200)
            if status == 'FAILED':

                return Response({"Failed": "Payment failed, please place order again "}, status=200)
            

            if status == 'PENDING':
                return Response({"Pending": "Payment pending. Please dial *126# and confirm payment then click the confirm Pay button bellow"}, status=200)
           
            return Response({"Not_Found": "Order Not found"}, status=404)

class BuyOrderView(generics.ListAPIView):
    serializer_class = OrderViewSerializer
    queryset = Order.objects.all()
    # permission_classes = []

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.filter(buyer = user, payment_status = 'SUCCESSFUL' )
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
        print(request.data)
        code = request.data['code']
        
        if order.code == code:
            order.delivered = True
            order.save()
            account = Account.objects.get(shop = order.item.shop)
            account.pending_balance -= order.total
            account.available_balance += order.total
            account.save()

            return Response(
                {
                    'success':'Item delivered successfully',
                }, status=status.HTTP_200_OK
            )
        return Response(
                {
                    'failed':'Incorrect Delivery Code',
                    
                }, status=status.HTTP_400_BAD_REQUEST
            )
    
class ViewItems(generics.ListAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
    # permission_classes=[]

    def get_queryset(self):
        id = self.kwargs['id']
        qs= Item.objects.filter(shop__id = id)
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

class UserShopView(generics.RetrieveAPIView):
    serializer_class = ShopSerializer

    def get_object(self):
        shop = Shop.objects.get(owner = self.request.user)
        return  shop
    # queryset = Shop.objects.all()
    # lookup_field = 'id'

class WithdrawalRequest(generics.ListCreateAPIView):
    serializer_class = WithdrawalRequestSerializer
    permission_classes = []
    

    def get_queryset(self):
        id = self.kwargs['id']
        qs = Withdrawal.objects.filter(shop__id = id)
        return qs
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(
            {
                'success':'Withdrawal request placed successfully'
            }, status=status.HTTP_201_CREATED
        )
    
    def get_serializer_context(self):
        context =  super().get_serializer_context()
        context['id'] = self.kwargs['id']
        return context



#  def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data = request.data)
#         serializer.is_valid(raise_exception = True)
#         serializer.save()
#         return Response({
#             'success':'Order placed successfully. Dial *126# and confirm payment then click the Confirm Pay button below'
#         },  status=status.HTTP_201_CREATED)

class PaymentNotification(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        res = request.data
        # print(res)
        # send_mail(
        #     message= f'{res}',
        #     subject='payment_confirm',
        #     # from_email=''
        #     from_email = settings.DEFAULT_FROM_EMAIL,
        #     recipient_list = [settings.DEFAULT_FROM_EMAIL],

        # )

        # return Response({
        #     'email sent':f'{res} email has been sent'
        # },  status=status.HTTP_201_CREATED)
        data = request.data
        # data = data.get('data')
        transaction_id = data.get('transaction_id')
        status = data.get("transaction_status", "UNKNOWN")
        print('status', status)
        # message = data.get('message')
        order = Order.objects.get(payment_id = transaction_id)
        order.payment_status = status
        order.save()
        print('order is ',order.item.shop.owner.email)
        
        if status == 'SUCCESSFUL':
            account = Account.objects.get(shop__id = order.item.shop.id)
            account.pending_balance += int(order.total)
            account.save()
            print('here')
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
            return Response({"Success": "Payment completed"}, status=200)
        if status == 'FAILED':

            return Response({"Failed": "Payment failed, please place order again "}, status=200)
        

        if status == 'PENDING':
            return Response({"Pending": "Payment pending. Please dial *126# and confirm payment then click the confirm Pay button bellow"}, status=200)
        
        return Response({"Not_Found": "Order Not found"}, status=404)
    
class ShopListingView(generics.ListAPIView):
    serializer_class = ShopSerializer

    def get_queryset(self):
        qs = Shop.objects.filter(is_verified = True)
        return qs


#Refund Functionality

class RefundCreateAPIView(generics.CreateAPIView):
    serializer_class = RefundSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Refund.objects.filter(user=self.request.user)
#For users to see their refund requests   
class RefundListAPIView(generics.ListAPIView):
    serializer_class = RefundSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Refund.objects.filter(user=self.request.user)


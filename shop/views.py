from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, viewsets
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from .models import Refund


from rest_framework.permissions import IsAuthenticated 
#serializers
from .serializers import ShopCreationSerializer, OrderSerializer, OrderViewSerializer, ItemViewSerializer, ShopSerializer, WithdrawalRequestSerializer, AccountSerializer
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
        print(request.data)
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
                reseller_account = Account.objects.get(shop__id = order.item.shop.id)
                if order.item.is_resale:
                    # If the item is a resale, we need to get the original shop account
                    original_item = order.item.original_item
                    original_shop = original_item.shop
                    original_account = Account.objects.get(shop__id = original_shop.id)
                    # Calculate profit and update accounts
                    profit = int(order.total) - int(original_item.price)*int(order.quantity)
                    reseller_account.pending_balance += int(profit)
                    reseller_account.save()
                    original_account.pending_balance += int(original_item.price)*int(order.quantity)
                    original_account.save()
                else:
                    # If the item is not a resale, just update the reseller account
                    reseller_account.pending_balance += int(order.total)
                    reseller_account.save()
                # account = Account.objects.get(shop__id = order.item.shop.id)
                # account.pending_balance += int(order.total)
                # account.save()
                    print('here')
                    print('account is ',reseller_account)
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
        qs = Order.objects.filter(
            Q(item__shop__id = shop_id) |
            Q(item__original_item__shop__id = shop_id)
            )
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
            if order.item.is_resale:
                resell_item = order.item
                original_item = order.item.original_item
                # original_item = order.item.original_item
                original_shop = original_item.shop
                original_account = Account.objects.get(shop__id = original_shop.id)
                # Calculate profit and update accounts
                profit = int(order.total) - int(original_item.price)*int(order.quantity)
                reseller_account = Account.objects.get(shop__id = order.item.shop.id)
                reseller_account.available_balance += int(profit)
                reseller_account.pending_balance -= int(profit)
                resell_item.total_sold  += int(profit)
                resell_item.count += int(order.quantity)
                resell_item.save()
                original_item.total_sold  += int(order.total)
                original_item.count += int(order.quantity)
                original_item.save()
                reseller_account.save()
                original_account.available_balance += int(original_item.price)*int(order.quantity)
                original_account.pending_balance -= int(original_item.price)*int(order.quantity)
                original_account.save()
                subject = f'Order delivered for {order.item}'
                message = f'An order has been delivered for {order.quantity} quantity of {order.item.name}. You can now access your funds'
                send_mail(
                    subject=subject,
                    message=message,
                    recipient_list=[order.item.original_item.shop.owner.email], 
                    from_email=settings.DEFAULT_FROM_EMAIL,
                )
            else:
                account = Account.objects.get(shop__id = order.item.shop.id)
                account.available_balance += int(order.total)
                account.pending_balance -= int(order.total)
            order.save()
            subject = f'Order delivered for {order.item}'
            message = f'An order has been delivered for {order.quantity} quantity of {order.item.name}. You can now access your funds'
            send_mail(
                subject=subject,
                message=message,
                recipient_list=[order.item.shop.owner.email], 
                from_email=settings.DEFAULT_FROM_EMAIL,
            )
            print('Order delivered successfully')
            
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
    serializer_class = ItemSerializer
    filter_backends = (SearchFilter,)
    search_fields = ['name', 'category__name', 'sub_category__name', 'secret_code']

    def get_queryset(self):
        queryset = Item.objects.filter(shop__is_verified=True)

        search_query = self.request.query_params.get('search', None)
        if search_query:
            # Return:
            # 1) Non-custom items matching search normally
            # OR
            # 2) Custom items only if secret_code matches the search query exactly (or contains)
            queryset = queryset.filter(
                Q(is_custom=False) & (
                    Q(name__icontains=search_query) | 
                    Q(category__name__icontains=search_query) |
                    Q(sub_category__name__icontains=search_query)|
                    Q(secret_code__icontains=search_query)
                ) | 
                Q(is_custom=True, secret_code__icontains=search_query)
            )
        else:
            # No search query: just exclude all custom items
            queryset = queryset.filter(is_custom=False)

        return queryset


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


# Receive notification for successful payment
class PaymentNotification(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        res = request.data
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
        
        '''
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
            '''
        if status == 'SUCCESSFUL':
            reseller_account = Account.objects.get(shop__id = order.item.shop.id)
            if order.item.is_resale:
                # If the item is a resale, we need to get the original shop account
                original_item = order.item.original_item
                original_shop = original_item.shop
                original_account = Account.objects.get(shop__id = original_shop.id)
                # Calculate profit and update accounts
                profit = int(order.total) - int(original_item.price)*int(order.quantity)
                reseller_account.pending_balance += int(profit)
                reseller_account.save()
                original_account.pending_balance += int(original_item.price)*int(order.quantity)
                original_account.save()
                subject = f'Order placed for {order.item}'
                message = f'An order has been placed for {order.quantity} quantity of {order.item.name} as a resale from shop {order.item.original_item.shop.name}. The original shop has been credited with {int(original_item.price)*int(order.quantity)} and you have been credited with {int(profit)}. Please get to the buyer and deliver so you and the reseller can have access to your funds'
                # try:
                send_mail(
                    subject=subject,
                    message=message,
                    recipient_list=[order.item.shop.owner.email], 
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    )
                
                subject = f'Order placed for {order.item}'
                message = f'An order has been placed for {order.quantity} quantity of {order.item.name}. This is a reselling order. Please get to the buyer and deliver so you and the reseller can have access too your funds'
                # try:
                send_mail(
                    subject=subject,
                    message=message,
                    recipient_list=[order.item.original_item.shop.owner.email], 
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    )
            else:
                # If the item is not a resale, just update the reseller account
                reseller_account.pending_balance += int(order.total)
                reseller_account.save()
            # account = Account.objects.get(shop__id = order.item.shop.id)
            # account.pending_balance += int(order.total)
            # account.save()
                print('here')
                print('account is ',reseller_account)
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
    


#Shop money
class ShopAccountView(generics.RetrieveAPIView):
    serializer_class = AccountSerializer
    

    def get_object(self):
        user = self.request.user
        shop = Shop.objects.get(owner__id = user.id)
        account = Account.objects.get(shop = shop)
        return account

#Resale View

class ResaleItemView(APIView): 
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):
        try:
            original_item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({"error": "Original item not found."}, status=404)
        
        # Prevent reselling your own item
        if original_item.shop == Shop.objects.get(owner = request.user):  
            return Response({"error": "You cannot resell your own item."}, status=400)

        data = request.data.copy()
        data['name'] = original_item.name
        data['description'] = original_item.description
        data['is_resale'] = True
        # data['images'] = original_item.images
        # data['original_item'] = original_item.id
        # data['shop'] = Shop.objects.get(owner = request.user)

        serializer = ItemSerializer(data=data, context={'request': request, 'id':original_item.id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    #Handleing the Amont (Sharing Profit and Linking price to original shop)
class PurchaseItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({"error": "Item not found."}, status=404)

        # Get original item and original shop
        if item.is_resale and item.original_item:
            original_item = item.original_item
            original_shop = original_item.shop
            reseller = item.shop
            original_price = original_item.price
            amount_paid = item.price
            profit = amount_paid - original_price
            delivered_by = original_shop
        else:
            original_item = None
            original_shop = item.shop
            reseller = None
            original_price = item.price
            amount_paid = item.price
            profit = 0
            delivered_by = original_shop

        # You could add payment and validation logic here...

        # Save purchase info
        Item.objects.create(
            item=item,
            buyer=request.user,
            original_shop=original_shop,
            reseller=reseller,
            original_price=original_price,
            amount_paid=amount_paid,
            profit=profit,
            delivered_by=delivered_by,
        )

        return Response({
            "message": "Purchase successful.",
            "original_shop": original_shop.user.username,
            "reseller": reseller.user.username if reseller else None,
            "original_price": original_price,
            "amount_paid": amount_paid,
            "profit_to_reseller": profit,
            "delivery_by": delivered_by.user.username
        }, status=201)

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status

#serializers
from .serializers import ShopCreationSerializer, OrderSerializer, OrderViewSerializer
from .models import Order

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
            'success':'Order placed successfully'
        },  status=status.HTTP_201_CREATED)
    
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
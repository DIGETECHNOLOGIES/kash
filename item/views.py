from django.shortcuts import render,get_object_or_404
from rest_framework.generics import ListCreateAPIView,ListAPIView, RetrieveAPIView,DestroyAPIView,CreateAPIView,UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import *

# Create your views here.
class ItemList(ListAPIView):
    queryset=Item.objects.all()
    serializer_class=ItemSerializer
    permission_classes=[]
class ItemDetail(RetrieveAPIView):
    queryset=Item.objects.all()
    serializer_class=ItemSerializer
    lookup_field='pk'
    permission_classes=[]
class CreateItem(ListCreateAPIView):
    queryset=Item.objects.all()
    serializer_class=ItemSerializer
    lookup_field='pk'
    permission_classes=[]
class UpdateItem(UpdateAPIView):
    queryset=Item.objects.all()
    serializer_class=ItemSerializer
    lookup_field='pk'
    permission_classes=[]
class DeleteItem(DestroyAPIView):
    queryset=Item.objects.all()
    serializer_class=ItemSerializer
    lookup_field='pk'
    permission_classes=[]
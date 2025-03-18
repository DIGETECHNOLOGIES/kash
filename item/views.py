from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    ListAPIView, RetrieveAPIView, DestroyAPIView, CreateAPIView, UpdateAPIView
)
from rest_framework.permissions import IsAuthenticated
from .serializers import ItemSerializer
from shop.models import Item, Image


class ItemList(ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = []


class ItemDetail(RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'pk'
    permission_classes = []


class CreateItem(CreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = []

    def perform_create(self, serializer):
        images_data = self.request.FILES.getlist('images') 
        item = serializer.save()  
        for image_file in images_data:
            image = Image.objects.create(image=image_file)
            item.images.add(image)  


class UpdateItem(UpdateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'pk'
    permission_classes = []

    def perform_update(self, serializer):
        images_data = self.request.FILES.getlist('images')  
        item = serializer.save()

        for image_file in images_data:
            image = Image.objects.create(image=image_file)  
            item.images.add(image)


class DeleteItem(DestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'pk'
    permission_classes = []

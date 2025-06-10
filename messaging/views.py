from django.shortcuts import render
from rest_framework import generics
from .models import Message
from .serializers import MessageSerializer
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from shop.models import Shop

# Create your views here.
class MessageView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    # permission_classes= []
    

    def get_queryset(self):
        
        user = self.kwargs.get('user')
        shop = int(self.kwargs.get('shop'))
        print(f'{user} {shop} {self.request.user.id} ')
        try:
            if(self.request.user.id == user) or Shop.objects.get(id = shop).owner.id == self.request.user.id:
        
                messages = Message.objects.filter(Q(sender_user__id = user, receiver_shop__id = shop)|Q(sender_shop__id = shop, receiver_user__id = user))
                return messages
        except:
            return []

        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        response_serializer = self.get_serializer(message)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
class AllMessagesView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        shop = self.kwargs['shop']
        user = self.request.user
        messages = Message.objects.filter(
            Q(sender_user = user) |
            Q(receiver_user = user) |
            Q(sender_shop__id = shop) |
            Q(receiver_shop__id = shop)
            )
        return messages





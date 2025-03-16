from django.shortcuts import render
from rest_framework import generics
from .models import Message
from .serializers import MessageSerializer
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
class MessageView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes= []
    

    def get_queryset(self):
        user = self.kwargs.get('user')
        shop = self.kwargs.get('shop')
        messages = Message.objects.filter(Q(sender_user__id = user, receiver_shop__id = shop)|Q(sender_shop__id = shop, receiver_user__id = user))
        return messages

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response({
            'success':'Message sent successfully'
        },  status=status.HTTP_201_CREATED)




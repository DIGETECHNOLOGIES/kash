from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import  urlsafe_base64_decode
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import  force_str

from .models import User
from .tokens import account_activation_token
from .serializers import CreateUserSerializer, LoginSerializer, NewActivationLinkserializer, UserViewSerializer, email 



class RequestNewLinkView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = NewActivationLinkserializer

    @staticmethod
    def send_activation_email(user_email, username, user, request):
        email(user_email, username, user, request)

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email, is_active=False)
        except User.DoesNotExist:
            return Response({"message": "User not found or already activated."}, status=status.HTTP_400_BAD_REQUEST)

        self.send_activation_email(user.email, user.username, user, request)
        return Response({"message": "A new activation link has been sent to your email."}, status=status.HTTP_200_OK)


class ActivateAccountView(generics.GenericAPIView):
    permission_classes = []
    authentication_classes = []
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            user = None

        if user and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return render(request, 'confirm_activation.html',{"success": "Your account has been activated successfully!"}, status=status.HTTP_200_OK)
        return render(request, 'confirm_activation.html', {"failed": "Activation link is invalid or has expired. Please request a new link from the KASH app."}, status=status.HTTP_400_BAD_REQUEST)


class CreateUser(generics.CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'message': 'User registered successfully',
                'user': serializer.data
            }, status=status.HTTP_201_CREATED
        )


class Login(generics.GenericAPIView):
    permission_classes = []
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(request.data)
        serializer.is_valid(raise_exception=True)
        print(request.data)
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        if not User.objects.filter(email=email).exists():
            raise AuthenticationFailed('User with email does not exist.')

        user = authenticate(request, username=email, password=password)

        if user is None:
            if User.objects.filter(email=email, is_active=False).exists():
                raise AuthenticationFailed('Account has not yet been activated.')
            raise AuthenticationFailed('Email and password do not match.')

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }, status=status.HTTP_200_OK)
    
class UserDetails(generics.RetrieveAPIView):
    serializer_class = UserViewSerializer
    

    def get_object(self):
        user = self.request.user
        return user
    

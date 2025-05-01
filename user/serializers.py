from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import serializers
from django.db import transaction
from .validators import validate_email, validate_password, validate_number, validate_username
from django.core.mail import send_mail
from django.conf import settings
from .models import User
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
# from shop.serializers import LocationSerializer
from .tokens import account_activation_token

def email(user_email, username, user, request):
    token = account_activation_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    current_site = get_current_site(request)
    activation_link = f"http://{current_site.domain}/user/activate/{uid}/{token}/"

    subject = 'Activate Your Kash Account'
    html_message = render_to_string('activation_email.html', {
        'username': username,
        'activation_link': activation_link
    })

    send_mail(
        subject=subject,
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        html_message=html_message
    )

class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[validate_email])
    username = serializers.CharField(write_only=True, required=True, validators=[validate_username])
    # number = serializers.CharField(write_only=True, required=True, validators=[validate_number])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        request = self.context.get('request')

        with transaction.atomic(): 
            user = User.objects.create_user(**validated_data)
            user.is_active = False

            try:
                email(user.email, user.username, user=user, request=request)
                user.save()
            except Exception as e:
                raise serializers.ValidationError({'message': f'Error sending email: {str(e)}'})

        return user

class UserViewSerializer(serializers.ModelSerializer):
    # location = LocationSerializer()
    class Meta:
        model = User
        fields = ['id', 'email', 'image', 'number', 'location', 'username']



class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

class NewActivationLinkserializer(serializers.Serializer):
    email = serializers.CharField()

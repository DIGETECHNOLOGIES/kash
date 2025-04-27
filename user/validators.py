from rest_framework import serializers
# from .serializers import 


from.models import User

def validate_email(value):
    qs = User.objects.filter(email__exact = value)
    if qs.exists():
        raise serializers.ValidationError(f' account with email {value} already exixts')
    return value

def validate_password(value):
    if len(value) < 8:
        raise serializers.ValidationError('Passowrd is too short')
    try:
        password = int(value)
        raise serializers.ValidationError('Password should be amixture of letters and numbers')
    except:
        return value
    
def validate_username(value):
    qs = User.objects.filter(username = value)
    if qs.exists():
        raise serializers.ValidationError(f'User with username {value} already exists')

def validate_number(value):
    if len(value) != 9:
        raise serializers.ValidationError('number is not correct')
    print(value[:2])
    if str(value[:2]) != '67' and str(value[:2]) != '65' and str(value[:2]) != '69' and str(value[:2]) != '68' and str(value[:2]) != '62':
        raise serializers.ValidationError('number is not a Cameroon number ')
    try:
        int(value)
        return value
    except:
        raise serializers.ValidationError(f'{value} is not a valid phone number')

    
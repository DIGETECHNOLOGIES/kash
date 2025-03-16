import requests
import base64
from decouple import config


def initiate_payment(amount, id):
# Replace with your actual API key and secret
    api_key = config('API_USER')
    api_secret = config('API_PASSWORD')

    # Encode API key and secret for Basic Auth
    auth_string = f"{api_key}:{api_secret}"
    auth_encoded = base64.b64encode(auth_string.encode()).decode()

    # Define headers
    headers = {
        "x-api-key": config('API_KEY'),
        "mode": "live",
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth_encoded}"
    }

    # Define payload
    payload = {
        "total_amount": amount,
        "currency": "XAF",
        "transaction_id": f'{id}',
        # "return_url": "https://webhook.site/d457b2f3-dd71-4f04-9af5-e2fcf3be8f34",
        # "notify_url": "https://webhook.site/d457b2f3-dd71-4f04-9af5-e2fcf3be8f34",
        "payment_country": "CM"
    }

    # Base URL (replace with the correct PayUnit API endpoint)
    base_url = "https://gateway.payunit.net"

    # Make the request
    response = requests.post(f"{base_url}/api/gateway/initialize", json=payload, headers=headers)

    # Print response
    print(response.status_code)
    print(response.json()) 
    return response # If response is JSON


def confirm_payment(number, amount, id):

    
    api_key = config('API_USER')
    api_secret = config('API_PASSWORD')
    
    auth_string = f"{api_key}:{api_secret}"
    auth_encoded = base64.b64encode(auth_string.encode()).decode()

    # Define headers
    headers = {
        "x-api-key": config('API_KEY'),
        "mode": "live",
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth_encoded}"
    }

    
    print('3:',id)
    payload = {
        "gateway": "CM_MTNMOMO", 
        "amount": amount,
        "transaction_id": f'{id}',  
        # "return_url": "https://my.website.com/payunit/return",
        "phone_number": str(number),  
        "currency": "XAF",
        "paymentType": "ussd",
        # "notify_url": "https://webhook.site/d457b2f3-dd71-4f04-9af5-e2fcf3be8f34"
    }

    
    base_url = "https://gateway.payunit.net"

    
    response = requests.post(f"{base_url}/api/gateway/makepayment", json=payload, headers=headers)

    print(response.status_code)
    print(response.json())  
    return response

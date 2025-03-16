import requests

url = "https://api.monetbil.com/payment/v1/placePayment"

headers = {
    "Content-Type": "application/json"
}

data = {
    "service": "3xqlc3sp7qGNbMCBe83HRPrCD5uMPbgOzXnf1VtDeLxvqhDQWs5nzqjBlIodBbHz",
    "phonenumber": "677482442",
    "amount": "10",
    "notify_url": "https://kash-133m.onrender.com/shop/transaction/callback/"
}

response = requests.post(url, json=data, headers=headers, verify=False)

# Print response
print("Status Code:", response.status_code)
print("Response JSON:", response.text)

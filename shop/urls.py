from django.urls import path
from . import views

urlpatterns = [
    path('verify-shop/', views.VerifyShop.as_view()),
    path('place-order/', views.PlaceOrder.as_view()),
    path('buyer-orders/', views.BuyOrderView.as_view()),
    path('seller-orders/<str:shop_id>/', views.SellOrderView.as_view()),
]
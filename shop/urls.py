from django.urls import path
from . import views

urlpatterns = [
    path('verify-shop/', views.VerifyShop.as_view()),
    path('place-order/', views.PlaceOrder.as_view()),
]
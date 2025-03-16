from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
# router = DefaultRouter()
# router.register(r'items', views.SearchItems)

urlpatterns = [
    path('verify-shop/', views.VerifyShop.as_view()),
    path('place-order/', views.PlaceOrder.as_view()),
    path('buyer-orders/', views.BuyOrderView.as_view()),
    path('seller-orders/<str:shop_id>/', views.SellOrderView.as_view()),
    path('confirm-delivery/<str:order_id>/', views.ConfirmDelivery.as_view()),
    path('items/', views.ViewItems.as_view()),
    path('items-filter/', views.SearchItems.as_view({'get':'list'})),
    path('shop-details/<str:id>/', views.ShopView.as_view()),
    path('transaction/callback/', views.PaymentConfirmation.as_view())
]
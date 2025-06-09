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
    path('items/<str:id>/', views.ViewItems.as_view()),
    path('items-filter/', views.SearchItems.as_view({'get':'list'})),
    path('shop-details/<str:id>/', views.ShopView.as_view()),
    path('shop-details', views.UserShopView.as_view()),
    path('transaction_status/<str:id>/', views.PaymentConfirmation.as_view()),
    path('withdraw/<str:id>/', views.WithdrawalRequest.as_view()),
    path('transaction/callback/', views.PaymentNotification.as_view()),
    path('shops/', views.ShopListingView.as_view(), name = 'shop-listing'),
    path('refund/', views.RefundCreateAPIView.as_view(), name='refund_'),
    path('my-refunds/', views.RefundListAPIView.as_view(), name='my_refunds'),
    #Resale
    path('resale/<int:product_id>/', views.ResaleProductView.as_view(), name='resale-product'),


]
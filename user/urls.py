from django.urls import path
from . import views

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', views.CreateUser.as_view() ),
    path('log/', views.Login.as_view()),
    path('activate/<uidb64>/<token>/', views.ActivateAccountView.as_view(), name='account-activate'),
    path('request-new-link/', views.RequestNewLinkView.as_view(), name='request-new-link'),
    path('', views.UserDetails.as_view(), name = 'user-data'),
   

]
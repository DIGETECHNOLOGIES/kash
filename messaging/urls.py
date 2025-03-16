from django.urls import path
from . import views


urlpatterns = [
    path('<uuid:user>/<str:shop>/', views.MessageView.as_view()),
]
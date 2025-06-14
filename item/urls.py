from django.urls import path
from . import views
urlpatterns=[
    path('',views.ItemList.as_view()),
    path('<int:pk>/',views.ItemDetail.as_view()),
    path('create',views.CreateItem.as_view()),
    path('<int:pk>/update/',views.UpdateItem.as_view()),
    path('<int:pk>/delete/',views.DeleteItem.as_view()),
    path('categories/', views.CategoryList.as_view()),
]
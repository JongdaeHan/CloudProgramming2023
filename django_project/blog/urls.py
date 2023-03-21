# urlconf for blog
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('<int:post_num>/', views.single_post_page)
]
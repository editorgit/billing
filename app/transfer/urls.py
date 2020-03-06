from django.urls import path

from . import views

urlpatterns = [
    path('transfer/', views.ajax_transfer),
    path('signup/', views.ajax_signup),
    path('login/', views.ajax_login),
]

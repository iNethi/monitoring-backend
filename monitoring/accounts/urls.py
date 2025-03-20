# accounts/urls.py
from django.urls import path
from .views import RegisterView, LocalLoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LocalLoginView.as_view(), name='login'),
]

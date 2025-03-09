# accounts/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # User profiles endpoints
    path('profile/', views.user_profile, name='profile'),
    
    # Wallet endpoints
    path('wallet/', views.wallet_detail, name='wallet'),
    path('wallet/deposit/', views.deposit, name='deposit'),
    path('wallet/withdraw/', views.withdraw, name='withdraw'),
    path('wallet/transfer/', views.transfer, name='transfer'),
    
    # Transactions endpoints
    path('transactions/', views.transaction_list, name='transactions'),
]
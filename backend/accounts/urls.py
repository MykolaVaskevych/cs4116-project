# accounts/urls.py

from django.urls import path, include
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from . import views
from .views import ReviewListCreateView, ReviewDetailView

# Create a router for viewsets
router = DefaultRouter()
router.register(r'services', views.ServiceViewSet)
router.register(r'inquiries', views.InquiryViewSet)
router.register(r'messages', views.InquiryMessageViewSet, basename='inquiry-messages')

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

    #reviews endpoints
    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
    
    # Include routers for the new viewsets
    path('', include(router.urls)),
]
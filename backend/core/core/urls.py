from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import ListPendingProvidersView, ApproveProviderView


from accounts.views import (
    RegisterView, LoginView, ProfileView, ChangePasswordView,
    RequestBusinessAccountView, ApproveProviderView
)
from services.views import (
    CreateServiceView, ApproveServiceView, RejectServiceView,
    CreateBookingView, UpdateBookingStatusView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change_password'),

    # Provider Approvals
    path('api/request-business/', RequestBusinessAccountView.as_view(), name='request_business'),
    path('api/approve-provider/<int:user_id>/', ApproveProviderView.as_view(), name='approve_provider'),

    # Services
    path('api/services/create/', CreateServiceView.as_view(), name='create_service'),
    path('api/services/<int:pk>/approve/', ApproveServiceView.as_view(), name='approve_service'),
    path('api/services/<int:pk>/reject/', RejectServiceView.as_view(), name='reject_service'),

    # Bookings (like inquiries/orders)
    path('api/bookings/create/', CreateBookingView.as_view(), name='create_booking'),
    path('api/bookings/<int:pk>/update-status/', UpdateBookingStatusView.as_view(), name='update_booking_status'),

    path('api/pending-providers/', ListPendingProvidersView.as_view(), name='pending_providers_list'),
    path('api/approve-provider/<int:user_id>/', ApproveProviderView.as_view(), name='approve_provider'),
    

    path('', lambda req: HttpResponse("This is the Urban Life Hub API root...")),
]

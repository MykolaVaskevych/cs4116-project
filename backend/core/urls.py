"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import LoginView

# Simple health check for Railway deployment
def health_check(request):
    return HttpResponse("OK")

# Create a custom admin login view with CSRF exemption for Railway deployment
admin.site.login = csrf_exempt(admin.site.login)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls", namespace="accounts")),
    path("api/health/", health_check, name="health_check"),
]

# Serve media and static files (both in development and production for Railway)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

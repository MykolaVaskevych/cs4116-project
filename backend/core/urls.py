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
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView

# Simple health check for Railway deployment
def health_check(request):
    return HttpResponse("OK")

# Create a custom admin login view with CSRF exemption for Railway deployment
admin.site.login = csrf_exempt(admin.site.login)

# Direct login endpoint for troubleshooting
@csrf_exempt
def direct_login(request):
    """Direct login endpoint that bypasses Django admin login form"""
    if request.method == 'GET':
        # Show a simple login form
        return HttpResponse('''
        <html>
            <head><title>Direct Admin Login</title></head>
            <body>
                <h1>Direct Admin Login</h1>
                <form method="post" action="/direct-login/">
                    <label>Email: <input type="email" name="email" value="admin@example.com"></label><br>
                    <label>Password: <input type="password" name="password" value="UrbanLife2025!"></label><br>
                    <button type="submit">Login</button>
                </form>
            </body>
        </html>
        ''')
    
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Try to authenticate
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Log the user in
            login(request, user)
            # Redirect to admin
            return redirect('/admin/')
        else:
            # Return login failure info
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Check user exists
            user_exists = User.objects.filter(email=email).exists()
            if user_exists:
                user = User.objects.get(email=email)
                user_info = {
                    'exists': True,
                    'email': user.email,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'password_issue': True,
                }
            else:
                user_info = {'exists': False}
                
            return JsonResponse({
                'authenticated': False,
                'email': email,
                'user_info': user_info,
                'message': 'Authentication failed. Check user info for details.'
            })

@csrf_exempt
def create_admin(request):
    """Endpoint to create an admin user directly from web"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Admin credentials
    username = 'admin'
    email = 'admin@example.com'
    password = 'UrbanLife2025!'
    
    try:
        # Delete any existing admin users with this email
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            user.delete()
            deleted = True
        else:
            deleted = False
        
        # Create a fresh admin user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        
        # Make sure it has admin rights
        user.is_staff = True
        user.is_superuser = True
        user.role = User.Role.MODERATOR
        user.save()
        
        return JsonResponse({
            'success': True,
            'deleted_existing': deleted,
            'user': {
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'role': user.role,
            },
            'message': 'Admin user created successfully. Use the direct-login link to login.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls", namespace="accounts")),
    path("api/health/", health_check, name="health_check"),
    path("direct-login/", direct_login, name="direct_login"),
    path("create-admin/", create_admin, name="create_admin"),
]

# Serve media and static files (both in development and production for Railway)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Wallet

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'business_info')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'business_info')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Wallet)
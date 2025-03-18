from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncDay, TruncMonth
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from .models import (
    User, Service, Inquiry, Transaction,
    Wallet, Review, Category
)

import datetime
import json


class DashboardAdmin(admin.ModelAdmin):
    """
    Admin view for the dashboard showing platform statistics
    """
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='accounts_dashboard'),
            path('api/stats/', self.admin_site.admin_view(self.api_stats), name='accounts_api_stats'),
            path('api/transactions/', self.admin_site.admin_view(self.api_transactions), name='accounts_api_transactions'),
            path('api/services/', self.admin_site.admin_view(self.api_services), name='accounts_api_services'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        """
        View for the admin dashboard
        """
        if not request.user.is_staff:
            raise PermissionDenied
        
        # Get basic statistics
        total_users = User.objects.count()
        total_customers = User.objects.filter(role=User.Role.CUSTOMER).count()
        total_businesses = User.objects.filter(role=User.Role.BUSINESS).count()
        total_services = Service.objects.count()
        total_inquiries = Inquiry.objects.count()
        open_inquiries = Inquiry.objects.filter(status=Inquiry.Status.OPEN).count()
        total_reviews = Review.objects.count() 
        
        # Get wallet statistics
        wallet_sum = Wallet.objects.aggregate(Sum('balance'))['balance__sum'] or 0
        
        # Get top-rated services
        top_services = Service.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).filter(
            review_count__gt=0
        ).order_by('-avg_rating')[:5]
        
        # Get top categories
        top_categories = Category.objects.annotate(
            service_count=Count('services')
        ).order_by('-service_count')[:5]
        
        # Get recent activity
        recent_inquiries = Inquiry.objects.all().order_by('-created_at')[:5]
        recent_reviews = Review.objects.all().order_by('-created_at')[:5]
        recent_transactions = Transaction.objects.all().order_by('-created_at')[:5]
        
        # Prepare the context
        context = {
            'title': _('Dashboard'),
            'stats': {
                'total_users': total_users,
                'total_customers': total_customers,
                'total_businesses': total_businesses,
                'total_services': total_services,
                'total_inquiries': total_inquiries,
                'open_inquiries': open_inquiries,
                'total_reviews': total_reviews,
                'wallet_total': float(wallet_sum),
            },
            'top_services': top_services,
            'top_categories': top_categories,
            'recent_inquiries': recent_inquiries,
            'recent_reviews': recent_reviews,
            'recent_transactions': recent_transactions,
        }
        
        return TemplateResponse(request, 'admin/dashboard.html', context)
    
    def api_stats(self, request):
        """API endpoint for dashboard statistics"""
        if not request.user.is_staff:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Get time range for statistics (last 30 days)
        end_date = timezone.now()
        start_date = end_date - datetime.timedelta(days=30)
        
        # Get daily user signups
        daily_signups = User.objects.filter(
            date_joined__gte=start_date,
            date_joined__lte=end_date
        ).annotate(
            day=TruncDay('date_joined')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # Get daily inquiry creation
        daily_inquiries = Inquiry.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # Format the data for the chart
        dates = [(start_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d') 
                 for i in range((end_date - start_date).days + 1)]
        
        # Initialize data with zeros
        signups_data = {date: 0 for date in dates}
        inquiries_data = {date: 0 for date in dates}
        
        # Fill in actual data
        for item in daily_signups:
            date_str = item['day'].strftime('%Y-%m-%d')
            signups_data[date_str] = item['count']
            
        for item in daily_inquiries:
            date_str = item['day'].strftime('%Y-%m-%d')
            inquiries_data[date_str] = item['count']
        
        return JsonResponse({
            'dates': dates,
            'signups': list(signups_data.values()),
            'inquiries': list(inquiries_data.values()),
        })
    
    def api_transactions(self, request):
        """API endpoint for transaction data"""
        if not request.user.is_staff:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Get time range for statistics (last 6 months)
        end_date = timezone.now()
        start_date = end_date - datetime.timedelta(days=180)
        
        # Group transactions by month and type
        monthly_transactions = Transaction.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month', 'transaction_type').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('month', 'transaction_type')
        
        # Format data for the chart
        months = []
        deposits = []
        withdrawals = []
        transfers = []
        
        current = start_date.replace(day=1)
        while current <= end_date:
            month_str = current.strftime('%Y-%m')
            months.append(current.strftime('%b %Y'))
            
            # Find data for this month
            deposit_amount = 0
            withdrawal_amount = 0
            transfer_amount = 0
            
            for item in monthly_transactions:
                if item['month'].strftime('%Y-%m') == month_str:
                    if item['transaction_type'] == 'DEPOSIT':
                        deposit_amount = float(item['total'])
                    elif item['transaction_type'] == 'WITHDRAWAL':
                        withdrawal_amount = float(item['total'])
                    elif item['transaction_type'] == 'TRANSFER':
                        transfer_amount = float(item['total'])
            
            deposits.append(deposit_amount)
            withdrawals.append(withdrawal_amount)
            transfers.append(transfer_amount)
            
            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        return JsonResponse({
            'months': months,
            'deposits': deposits,
            'withdrawals': withdrawals,
            'transfers': transfers,
        })
    
    def api_services(self, request):
        """API endpoint for service statistics"""
        if not request.user.is_staff:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Get services by category
        category_services = Category.objects.annotate(
            service_count=Count('services')
        ).values('name', 'service_count').order_by('-service_count')
        
        # Format data for chart
        categories = [item['name'] for item in category_services]
        service_counts = [item['service_count'] for item in category_services]
        
        # Get rating distribution
        rating_distribution = Review.objects.values('rating').annotate(
            count=Count('rating')
        ).order_by('rating')
        
        # Format rating data
        ratings = [str(i) for i in range(6)]  # 0-5 stars
        rating_counts = [0, 0, 0, 0, 0, 0]  # Initialize with zeros
        
        for item in rating_distribution:
            rating_counts[item['rating']] = item['count']
        
        return JsonResponse({
            'categories': {
                'labels': categories,
                'data': service_counts,
            },
            'ratings': {
                'labels': ratings,
                'data': rating_counts,
            }
        })

# Don't register this as a model, it's just for the dashboard
# admin.site.register(DashboardAdmin)
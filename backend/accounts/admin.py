from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Avg, Count
from decimal import Decimal
from django import forms
from .models import (
    User, Wallet, Transaction, Category, Service, 
    Inquiry, InquiryMessage, Review, ReviewComment
)


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'wallet_balance', 'is_staff', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'profile_image', 'bio')}),
        ('Role and Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role'),
        }),
    )
    
    def wallet_balance(self, obj):
        """Display wallet balance with a link to the wallet admin page"""
        try:
            wallet = obj.wallet
            url = reverse('admin:accounts_wallet_change', args=[wallet.id])
            return format_html('<a href="{}">${}</a>', url, wallet.balance)
        except Wallet.DoesNotExist:
            return "$0.00"
    wallet_balance.short_description = "Wallet Balance"
    
    def save_model(self, request, obj, form, change):
        """When creating a user, ensure a wallet is created"""
        created = not obj.pk
        super().save_model(request, obj, form, change)
        
        # Create wallet for new users if it doesn't exist
        if created and not hasattr(obj, 'wallet'):
            Wallet.objects.create(user=obj)


class WalletTransactionInline(admin.TabularInline):
    model = Transaction
    fk_name = 'from_wallet'
    verbose_name = 'Outgoing Transaction'
    verbose_name_plural = 'Outgoing Transactions'
    extra = 0
    fields = ('transaction_id', 'transaction_type', 'to_wallet', 'amount', 'created_at')
    readonly_fields = ('transaction_id', 'transaction_type', 'to_wallet', 'amount', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


class WalletReceiveTransactionInline(admin.TabularInline):
    model = Transaction
    fk_name = 'to_wallet'
    verbose_name = 'Incoming Transaction'
    verbose_name_plural = 'Incoming Transactions'
    extra = 0
    fields = ('transaction_id', 'transaction_type', 'from_wallet', 'amount', 'created_at')
    readonly_fields = ('transaction_id', 'transaction_type', 'from_wallet', 'amount', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'transaction_count', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [WalletTransactionInline, WalletReceiveTransactionInline]
    actions = ['add_funds', 'reset_balance']
    
    def transaction_count(self, obj):
        """Count all transactions involving this wallet"""
        outgoing = obj.sent_transactions.count()
        incoming = obj.received_transactions.count()
        return outgoing + incoming
    transaction_count.short_description = "Transactions"
    
    def add_funds(self, request, queryset):
        """Admin action to add $100 to selected wallets"""
        for wallet in queryset:
            wallet.deposit(Decimal('100.00'))
        self.message_user(request, f"Added $100.00 to {queryset.count()} wallets.")
    add_funds.short_description = "Add $100 to selected wallets"
    
    def reset_balance(self, request, queryset):
        """Admin action to reset wallet balance to $0"""
        for wallet in queryset:
            if wallet.balance > 0:
                wallet.withdraw(wallet.balance)
            elif wallet.balance < 0:
                wallet.deposit(abs(wallet.balance))
        self.message_user(request, f"Reset balance to $0.00 for {queryset.count()} wallets.")
    reset_balance.short_description = "Reset balance to $0"


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'transaction_type', 'from_user', 'to_user', 'amount', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('transaction_id', 'from_wallet__user__email', 'to_wallet__user__email')
    readonly_fields = ('transaction_id', 'from_wallet', 'to_wallet', 'amount', 'transaction_type', 'created_at')
    
    def from_user(self, obj):
        """Display sender with link to user admin page"""
        if obj.from_wallet:
            url = reverse('admin:accounts_user_change', args=[obj.from_wallet.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.from_wallet.user.email)
        return "-"
    from_user.short_description = "From"
    
    def to_user(self, obj):
        """Display recipient with link to user admin page"""
        if obj.to_wallet:
            url = reverse('admin:accounts_user_change', args=[obj.to_wallet.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.to_wallet.user.email)
        return "-"
    to_user.short_description = "To"
    
    def has_add_permission(self, request):
        """Don't allow direct creation of transactions from admin panel"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Don't allow changing transactions"""
        return False


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'service_count', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def service_count(self, obj):
        """Display count of services in this category"""
        count = obj.services.count()
        return count
    service_count.short_description = "Services"


class ServiceAdminForm(forms.ModelForm):
    """Custom form for ServiceAdmin with validation"""
    
    class Meta:
        model = Service
        fields = '__all__'
        
    def clean(self):
        """Custom validation for service creation"""
        cleaned_data = super().clean()
        
        business = cleaned_data.get('business')
        if business and not business.is_business:
            self.add_error('business', 'Only business users can create services')
        
        return cleaned_data


class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm
    list_display = ('name', 'business', 'category', 'avg_rating', 'review_count', 'created_at')
    list_filter = ('category', 'created_at', 'business__email')
    search_fields = ('name', 'description', 'business__email', 'business__username')
    readonly_fields = ('created_at', 'updated_at')
    
    def avg_rating(self, obj):
        """Display average rating with star symbols"""
        avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        if avg is None:
            return "No ratings"
        
        # Round to nearest half star
        rounded = round(avg * 2) / 2
        
        # Display stars (★) for the rating
        full_stars = int(rounded)
        half_star = rounded - full_stars > 0
        stars = '★' * full_stars
        if half_star:
            stars += '½'
            
        return f"{stars} ({avg:.1f})"
    avg_rating.short_description = "Rating"
    
    def review_count(self, obj):
        """Display number of reviews for this service"""
        return obj.reviews.count()
    review_count.short_description = "Reviews"
    
    def save_model(self, request, obj, form, change):
        """Handle validation errors gracefully"""
        try:
            super().save_model(request, obj, form, change)
        except ValueError as e:
            self.message_user(request, str(e), level='error')


class InquiryMessageInline(admin.TabularInline):
    model = InquiryMessage
    extra = 1
    fields = ('sender', 'content', 'created_at')
    readonly_fields = ('created_at',)


class InquiryAdmin(admin.ModelAdmin):
    list_display = ('subject', 'service', 'customer', 'status', 'moderator', 'message_count', 'created_at')
    list_filter = ('status', 'created_at', 'service__name')
    search_fields = ('subject', 'customer__email', 'service__name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [InquiryMessageInline]
    actions = ['close_inquiries', 'reopen_inquiries']
    
    def message_count(self, obj):
        """Display number of messages in this inquiry"""
        return obj.messages.count()
    message_count.short_description = "Messages"
    
    def close_inquiries(self, request, queryset):
        """Admin action to close selected inquiries"""
        moderator = request.user
        if not moderator.is_moderator:
            # Make admin users moderators for this action
            if moderator.is_superuser:
                moderator.role = User.Role.MODERATOR
            else:
                self.message_user(request, "Only moderators can close inquiries.", level='error')
                return
                
        for inquiry in queryset.filter(status=Inquiry.Status.OPEN):
            inquiry.close(moderator)
        
        closed_count = queryset.filter(status=Inquiry.Status.CLOSED).count()
        self.message_user(request, f"Closed {closed_count} inquiries.")
    close_inquiries.short_description = "Close selected inquiries"
    
    def reopen_inquiries(self, request, queryset):
        """Admin action to reopen selected inquiries"""
        for inquiry in queryset.filter(status=Inquiry.Status.CLOSED):
            inquiry.status = Inquiry.Status.OPEN
            inquiry.save(update_fields=['status', 'updated_at'])
        
        reopened_count = queryset.filter(status=Inquiry.Status.OPEN).count()
        self.message_user(request, f"Reopened {reopened_count} inquiries.")
    reopen_inquiries.short_description = "Reopen selected inquiries"


class InquiryMessageAdminForm(forms.ModelForm):
    """Custom form for InquiryMessageAdmin with validation"""
    
    class Meta:
        model = InquiryMessage
        fields = '__all__'
        
    def clean(self):
        """Check if the inquiry is closed"""
        cleaned_data = super().clean()
        
        # Only check when creating new messages
        if not self.instance.pk:
            inquiry = cleaned_data.get('inquiry')
            
            if inquiry and inquiry.status == 'CLOSED':
                self.add_error('inquiry', 'Cannot add messages to a closed inquiry')
        
        return cleaned_data


class InquiryMessageAdmin(admin.ModelAdmin):
    form = InquiryMessageAdminForm
    list_display = ('inquiry_subject', 'sender', 'content_preview', 'created_at')
    list_filter = ('created_at', 'inquiry__status')
    search_fields = ('content', 'sender__email', 'inquiry__subject')
    readonly_fields = ('created_at',)
    
    def inquiry_subject(self, obj):
        """Display inquiry subject with link to inquiry admin page"""
        url = reverse('admin:accounts_inquiry_change', args=[obj.inquiry.id])
        return format_html('<a href="{}">{}</a>', url, obj.inquiry.subject)
    inquiry_subject.short_description = "Inquiry"
    
    def content_preview(self, obj):
        """Display truncated message content"""
        max_length = 50
        if len(obj.content) > max_length:
            return f"{obj.content[:max_length]}..."
        return obj.content
    content_preview.short_description = "Message"
    
    def save_model(self, request, obj, form, change):
        """Handle validation errors gracefully"""
        try:
            super().save_model(request, obj, form, change)
        except ValueError as e:
            self.message_user(request, str(e), level='error')


class ReviewCommentInline(admin.TabularInline):
    model = ReviewComment
    extra = 1
    fields = ('author', 'content', 'created_at')
    readonly_fields = ('created_at',)


class ReviewAdminForm(forms.ModelForm):
    """Custom form for ReviewAdmin with custom validation"""
    
    class Meta:
        model = Review
        fields = '__all__'
        
    def clean(self):
        """Custom validation for reviews"""
        cleaned_data = super().clean()
        
        # Only check for new reviews (not editing)
        if not self.instance.pk:
            service = cleaned_data.get('service')
            user = cleaned_data.get('user')
            
            if service and user:
                # Check if user has a closed inquiry for this service
                from .models import Inquiry
                has_closed_inquiry = Inquiry.objects.filter(
                    customer=user, 
                    service=service, 
                    status=Inquiry.Status.CLOSED
                ).exists()
                
                if not has_closed_inquiry:
                    self.add_error('user', 
                        'This user does not have a closed inquiry for this service and cannot review it.'
                    )
                
                # Check for duplicate reviews
                from .models import Review
                has_review = Review.objects.filter(
                    user=user, 
                    service=service
                ).exists()
                
                if has_review:
                    self.add_error('user', 
                        'This user has already reviewed this service.'
                    )
        
        return cleaned_data


class ReviewAdmin(admin.ModelAdmin):
    form = ReviewAdminForm
    list_display = ('review_id', 'service', 'user', 'rating_stars', 'comment_preview', 'created_at')
    list_filter = ('rating', 'created_at', 'service__name')
    search_fields = ('comment', 'user__email', 'service__name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ReviewCommentInline]
    
    def rating_stars(self, obj):
        """Display rating with star symbols"""
        return '★' * obj.rating
    rating_stars.short_description = "Rating"
    
    def comment_preview(self, obj):
        """Display truncated review comment"""
        if not obj.comment:
            return "No comment"
            
        max_length = 50
        if len(obj.comment) > max_length:
            return f"{obj.comment[:max_length]}..."
        return obj.comment
    comment_preview.short_description = "Comment"
    
    def has_delete_permission(self, request, obj=None):
        """Allow moderators and admins to delete reviews"""
        return request.user.is_superuser or request.user.is_moderator
        
    def save_model(self, request, obj, form, change):
        """
        Override save_model to handle the custom validation rules
        for reviews gracefully in the admin interface
        """
        try:
            super().save_model(request, obj, form, change)
        except ValueError as e:
            # Convert ValueError from model validation to form error
            self.message_user(request, str(e), level='error')
            # Don't raise the exception further to prevent a 500 error


class ReviewCommentAdminForm(forms.ModelForm):
    """Custom form for ReviewCommentAdmin with validation"""
    
    class Meta:
        model = ReviewComment
        fields = '__all__'
        
    def clean(self):
        """Check if the author can comment on this review"""
        cleaned_data = super().clean()
        
        # Only check when creating new comments
        if not self.instance.pk:
            review = cleaned_data.get('review')
            author = cleaned_data.get('author')
            
            if review and author:
                # Ensure author is either the service owner or a moderator
                is_service_owner = (author == review.service.business)
                is_moderator = author.is_moderator
                
                if not (is_service_owner or is_moderator):
                    self.add_error('author', 
                        'Only service owners and moderators can comment on reviews'
                    )
        
        return cleaned_data


class ReviewCommentAdmin(admin.ModelAdmin):
    form = ReviewCommentAdminForm
    list_display = ('comment_id', 'review_service', 'author', 'content_preview', 'created_at')
    list_filter = ('created_at', 'author__email')
    search_fields = ('content', 'author__email', 'review__service__name')
    readonly_fields = ('created_at', 'updated_at')
    
    def review_service(self, obj):
        """Display the service being reviewed with link to review"""
        url = reverse('admin:accounts_review_change', args=[obj.review.review_id])
        return format_html('<a href="{}">{}</a>', url, obj.review.service.name)
    review_service.short_description = "Service Review"
    
    def content_preview(self, obj):
        """Display truncated comment content"""
        max_length = 50
        if len(obj.content) > max_length:
            return f"{obj.content[:max_length]}..."
        return obj.content
    content_preview.short_description = "Comment"
    
    def save_model(self, request, obj, form, change):
        """Handle validation errors gracefully"""
        try:
            super().save_model(request, obj, form, change)
        except ValueError as e:
            self.message_user(request, str(e), level='error')


# Register all models with their admin classes
admin.site.register(User, CustomUserAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Inquiry, InquiryAdmin)
admin.site.register(InquiryMessage, InquiryMessageAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(ReviewComment, ReviewCommentAdmin)
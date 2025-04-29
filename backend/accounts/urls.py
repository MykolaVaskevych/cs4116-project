# accounts/urls.py

from django.urls import path, include
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    ServiceReviewListView, ServiceReviewCreateView, UserReviewListView,
    ReviewDetailView, ReviewCommentListCreateView, ReviewCommentDetailView,
    BlogCategoryViewSet, BlogPostViewSet, BlogPostBySlugView, 
    BlogCommentListCreateView, BlogCommentDetailView, UserBlogPostListView,
    ModeratorListView, ModeratorRequestView, PaymentRequestListCreateView,
    PaymentRequestDetailView, PendingPaymentRequestListView, PaymentRequestActionView,
    ConversationListCreateView, ConversationDetailView, ConversationActionView,
    ConversationMessageListCreateView, UnreadConversationCountView,
    SupportTicketListCreateView, SupportTicketDetailView, SupportTicketCloseView,
    SupportMessageListCreateView, SupportUnreadCountView
)
from .service_reports import report_service

# Create a router for viewsets
router = DefaultRouter()
router.register(r'services', views.ServiceViewSet, basename='service')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'inquiries', views.InquiryViewSet, basename='inquiry')
router.register(r'messages', views.InquiryMessageViewSet, basename='inquiry-messages')
router.register(r'blog/categories', BlogCategoryViewSet, basename='blog-category')
router.register(r'blog/posts', BlogPostViewSet, basename='blog-post')

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # User profiles endpoints
    path('profile/', views.user_profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Wallet endpoints
    path('wallet/', views.wallet_detail, name='wallet'),
    path('wallet/deposit/', views.deposit, name='deposit'),
    path('wallet/withdraw/', views.withdraw, name='withdraw'),
    path('wallet/transfer/', views.transfer, name='transfer'),
    
    # Transactions endpoints
    path('transactions/', views.transaction_list, name='transactions'),

    # Reviews endpoints - RESTful nested resources
    # Service Reviews
    path('services/<int:service_pk>/reviews/', ServiceReviewListView.as_view(), name='service-reviews-list'),
    path('services/<int:service_pk>/reviews/create/', ServiceReviewCreateView.as_view(), name='service-review-create'),
    path('services/<int:service_pk>/reviews/<int:review_pk>/', ReviewDetailView.as_view(), name='service-review-detail'),
    
    # User Reviews
    path('users/<int:user_pk>/reviews/', UserReviewListView.as_view(), name='user-reviews-list'),
    
    # Direct Review access (for updates/deletion by owner)
    path('reviews/<int:review_pk>/', ReviewDetailView.as_view(), name='review-detail'),
    
    # Review Comments
    path('reviews/<int:review_pk>/comments/', ReviewCommentListCreateView.as_view(), name='review-comments-list'),
    path('reviews/<int:review_pk>/comments/<int:comment_pk>/', ReviewCommentDetailView.as_view(), name='review-comment-detail'),
    
    # Blog endpoints
    # Blog posts by slug (for SEO-friendly URLs)
    path('blog/posts/slug/<slug:slug>/', BlogPostBySlugView.as_view(), name='blog-post-by-slug'),
    
    # User blog posts
    path('users/<int:user_pk>/blog-posts/', UserBlogPostListView.as_view(), name='user-blog-posts'),
    
    # Blog comments
    path('blog/posts/<int:blog_post_pk>/comments/', BlogCommentListCreateView.as_view(), name='blog-comments-list'),
    path('blog/comments/<int:comment_pk>/', BlogCommentDetailView.as_view(), name='blog-comment-detail'),
    
    # Moderator management endpoints
    path('moderators/', ModeratorListView.as_view(), name='moderator-list'),
    path('moderators/request/', ModeratorRequestView.as_view(), name='moderator-request'),
    
    # Payment request endpoints
    path('payment-requests/', PaymentRequestListCreateView.as_view(), name='payment-request-list-create'),
    path('payment-requests/pending/', PendingPaymentRequestListView.as_view(), name='pending-payment-requests'),
    path('payment-requests/<uuid:request_id>/', PaymentRequestDetailView.as_view(), name='payment-request-detail'),
    path('payment-requests/<uuid:request_id>/respond/', PaymentRequestActionView.as_view(), name='payment-request-action'),
    
    # Conversation endpoints
    path('conversations/', ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/unread-count/', UnreadConversationCountView.as_view(), name='unread-conversation-count'),
    path('conversations/<uuid:conversation_id>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<uuid:conversation_id>/respond/', ConversationActionView.as_view(), name='conversation-action'),
    path('conversations/<uuid:conversation_id>/messages/', ConversationMessageListCreateView.as_view(), name='conversation-messages'),
    
    # Support ticket endpoints
    path('support/tickets/', SupportTicketListCreateView.as_view(), name='support-ticket-list-create'),
    path('support/tickets/<uuid:ticket_id>/', SupportTicketDetailView.as_view(), name='support-ticket-detail'),
    path('support/tickets/<uuid:ticket_id>/close/', SupportTicketCloseView.as_view(), name='support-ticket-close'),
    path('support/tickets/<uuid:ticket_id>/messages/', SupportMessageListCreateView.as_view(), name='support-ticket-messages'),
    path('support/unread/', SupportUnreadCountView.as_view(), name='support-unread-count'),
    
    # Service reports
    path('services/<int:service_id>/report/', report_service, name='report-service'),
    
    # Include routers for the new viewsets
    path('', include(router.urls)),
]
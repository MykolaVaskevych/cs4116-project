"""
Service Reports API Views
Implements functionality for the moderator dashboard to view and manage service reports
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404

from .models import ServiceReport, Service, SupportTicket, SupportMessage, User
from .serializers import ServiceReportSerializer, ServiceReportReviewSerializer

class ServiceReportListView(generics.ListAPIView):
    """
    API endpoint for listing all service reports
    Only moderators can see all reports
    """
    serializer_class = ServiceReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Check if user is a moderator
        user = self.request.user
        if not user.is_authenticated or user.role != 'MODERATOR':
            return ServiceReport.objects.none()
            
        # Return all service reports, ordered by creation date (newest first)
        return ServiceReport.objects.all().order_by('-created_at')

class ServiceReportCreateView(generics.CreateAPIView):
    """
    API endpoint for users to create service reports
    """
    serializer_class = ServiceReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Set the reporter to the current user
        serializer.save(reporter=self.request.user)

class ServiceReportDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a specific service report
    Moderators can see any report, users can only see their own
    """
    serializer_class = ServiceReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'report_id'
    
    def get_queryset(self):
        user = self.request.user
        
        # Moderators can see all reports
        if user.role == 'MODERATOR':
            return ServiceReport.objects.all()
            
        # Regular users can only see their own reports
        return ServiceReport.objects.filter(reporter=user)

class ServiceReportReviewView(generics.GenericAPIView):
    """
    API endpoint for moderators to review service reports
    """
    serializer_class = ServiceReportReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def check_permissions(self, request):
        super().check_permissions(request)
        if not request.user.role == 'MODERATOR':
            self.permission_denied(
                request, 
                message="Only moderators can review service reports.",
            )
    
    def post(self, request, report_id):
        # Get the report
        report = get_object_or_404(ServiceReport, pk=report_id)
        
        # Validate the request data
        serializer = self.serializer_class(
            data=request.data,
            context={'report': report, 'request': request}
        )
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            approve = (action == 'approve')
            
            try:
                # Process the review
                result = report.review(request.user, approve)
                
                # Return the updated report
                updated_report = ServiceReportSerializer(report).data
                return Response(
                    {
                        "status": "success", 
                        "result": result,
                        "report": updated_report
                    },
                    status=status.HTTP_200_OK
                )
            except ValueError as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def report_service(request, service_id):
    """
    API endpoint for users to report a service
    Creates both a service report and a support ticket
    """
    # Get the service
    service = get_object_or_404(Service, pk=service_id)
    
    # Check if user is trying to report their own service
    if service.business == request.user:
        return Response(
            {"error": "You cannot report your own service"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get the reason from the request
    reason = request.data.get('reason', '')
    if not reason:
        return Response(
            {"error": "A reason is required for reporting a service"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create the report
    serializer = ServiceReportSerializer(
        data={'service': service.id, 'reason': reason},
        context={'request': request}
    )
    
    if serializer.is_valid():
        # Create the service report
        report = serializer.save(reporter=request.user)
        
        # Create a support ticket for this report
        ticket_title = f"Service Report: {service.business_name}"
        ticket = SupportTicket.objects.create(
            user=request.user,
            title=ticket_title
        )
        
        # Add the initial message with report details
        initial_message = (
            f"I would like to report the service '{service.business_name}' "
            f"for the following reason:\n\n{reason}"
        )
        
        SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            content=initial_message
        )
        
        return Response(
            {
                "status": "success", 
                "report": ServiceReportSerializer(report).data,
                "ticket_id": str(ticket.ticket_id)
            },
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""
Utility classes and functions for API views
"""

from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status


class StandardAPIResponse:
    """
    Helper class to standardize API responses
    """
    
    @staticmethod
    def success(data=None, message="Success"):
        """Return successful response"""
        return Response({
            'success': True,
            'data': data or {},
            'message': message,
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    @staticmethod
    def error(message, status_code=status.HTTP_400_BAD_REQUEST, data=None):
        """Return error response"""
        return Response({
            'success': False,
            'data': data or {},
            'message': message,
            'timestamp': timezone.now().isoformat()
        }, status=status_code)

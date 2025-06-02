from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..serializer import UserSerializer


class UserProfileView(APIView):
    """
    API endpoint for retrieving and updating user profile information
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Returns the authenticated user's profile information"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
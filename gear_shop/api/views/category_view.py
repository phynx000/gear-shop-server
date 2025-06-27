from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404

from ..models import Category
from ..serializer import CategorySerializer


class CategoryListCreateView(APIView):
    """
    API view to get all categories or create a new one
    """

    def get(self, request):
        """Get all categories"""
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class CategoryDetailView(APIView):
    """
    API view to retrieve, update or delete a category
    """

    def get(self, request, pk):
        """Get a specific category by ID"""
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)




class CategoryBySlugView(APIView):
    """
    API view to get a category by its slug
    """

    def get(self, request, slug):
        """Get a specific category by slug"""
        category = get_object_or_404(Category, slug=slug)
        serializer = CategorySerializer(category)
        return Response(serializer.data)
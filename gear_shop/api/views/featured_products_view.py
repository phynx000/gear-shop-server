# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Product, FeaturedProduct
from api.models.FeaturedProduct import FeaturedGroup
from api.serializer import ProductSerializer, FeaturedGroupSerializer


class FeaturedProductsAPIView(APIView):
    def get(self, request):
        products = Product.objects.filter(is_featured=True).order_by("-updated_at")[:10]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class FeaturedGroupAPIView(APIView):
    def get(self, request, group_name):
        try:
            group = FeaturedGroup.objects.prefetch_related('featured_products__product').get(name=group_name)
            if not group.is_active():
                return Response({"error": "Group is not active"}, status=status.HTTP_403_FORBIDDEN)
            serializer = FeaturedGroupSerializer(group)
            return Response(serializer.data)
        except FeaturedGroup.DoesNotExist:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
from rest_framework.response import Response
from rest_framework.views import APIView
from ..services.brand_service import BrandService
from ..serializer import BrandSerializer
from django.http import JsonResponse

class BrandListView(APIView):
    def get(self, request):
        brands = BrandService.get_all_brands()
        serializer = BrandSerializer(brands, many=True)
        return Response(serializer.data)
from rest_framework.response import Response
from rest_framework.views import APIView
from ..services.category_service import  CategoryService
from ..serializer import CategorySerializer

class CategoryListView(APIView):
    def  get(self, request):
        category = CategoryService.get_all_category()
        serializer = CategorySerializer(category, many=True)
        return Response(serializer.data)


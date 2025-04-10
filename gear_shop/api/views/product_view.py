from rest_framework.permissions import AllowAny, IsAuthenticated
import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..services.product_service import ProductService
from ..serializer import ProductSerializer, ProductImageSerializer

logger = logging.getLogger(__name__)


# view trả về danh sách tất cả sản phẩm
class ProductListView(APIView):
    permission_classes = [AllowAny]
    def  get(self, request):
        products = ProductService.get_all_products()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

#view để trả về 1 sản phẩm theo id
class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        product = ProductService.get_product_by_id(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)


# view trả về danh sách sản phẩm theo category ( danh mục)
class ProductByCategoryListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, category_id):
        try:
            products = ProductService.get_product_by_category(category_id)
            if not products.exists():
                return Response({"message": "Không có sản phẩm nào trong danh mục này."},
                                status=status.HTTP_404_NOT_FOUND)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductImageListView(APIView):
    def get(self, request, pk):
        product_image_list = ProductService.get_product_image_by_product(pk)
        serializer = ProductImageSerializer(product_image_list, many=True)
        return Response(serializer.data)

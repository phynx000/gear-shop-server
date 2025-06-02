from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Category, Product
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
        serializer = ProductSerializer(product)  #  Không dùng many=True
        return Response(serializer.data)


# view trả về danh sách sản phẩm theo category ( danh mục)
class ProductByCategoryListView(APIView):
    permission_classes = [AllowAny]
    # def get(self, request, category_id):
    #     try:
    #         products = ProductService.get_product_by_category(category_id)
    #         if not products.exists():
    #             return Response({"message": "Không có sản phẩm nào trong danh mục này."},
    #                             status=status.HTTP_404_NOT_FOUND)
    #         serializer = ProductSerializer(products, many=True)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, slug):
        try:
            category = get_object_or_404(Category, slug=slug)
            products = ProductService.get_product_by_category(category.id)

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


@api_view(['GET'])
def get_product_versions(request, product_id):
    """
    API lấy các phiên bản sản phẩm cùng product_group
    """
    try:
        # Lấy sản phẩm hiện tại
        current_product = Product.objects.get(id=product_id)

        # Lấy tất cả sản phẩm cùng product_group, trừ sản phẩm hiện tại
        if current_product.product_group:
            versions = Product.objects.filter(
                product_group=current_product.product_group
            ).exclude(id=product_id).order_by('version')

            # Serialize dữ liệu
            serializer = ProductSerializer(versions, many=True)

            return Response({
                'current_product': {
                    'id': current_product.id,
                    'name': current_product.name,
                    'version': current_product.version,
                    'product_group': current_product.product_group
                },
                'versions': serializer.data,
                'total_versions': versions.count() + 1  # +1 cho sản phẩm hiện tại
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'current_product': {
                    'id': current_product.id,
                    'name': current_product.name,
                    'version': current_product.version,
                    'product_group': current_product.product_group
                },
                'versions': [],
                'total_versions': 1
            }, status=status.HTTP_200_OK)

    except Product.DoesNotExist:
        return Response({
            'error': 'Sản phẩm không tồn tại'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

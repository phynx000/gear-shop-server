from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import json

from ..models import Category, Product
from ..models.products import ProductImage
from ..models.specification import Specification
from ..models.stock import Stock
from ..services.product_service import ProductService
from ..serializer import ProductSerializer, ProductImageSerializer, ProductColorSerializer, CategorySerializer, \
    BrandSerializer

logger = logging.getLogger(__name__)


# view trả về danh sách tất cả sản phẩm
class ProductListView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        products = ProductService.get_all_products()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)



# view để trả về 1 sản phẩm theo id
class ProductDetailView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, pk):
        product = ProductService.get_product_by_id(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)


# view trả về danh sách sản phẩm theo category (danh mục)
class ProductByCategoryListView(APIView):
    permission_classes = [AllowAny]

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


# class ProductImageView(APIView):
#     """
#     API view to manage product images
#     """
#     parser_classes = (MultiPartParser, FormParser)
#
#     def post(self, request, product_id):
#         """Add images to a product"""
#         # Only admin_site and staff can add images
#         if not request.user.is_authenticated or not (request.user.is_admin_user or request.user.is_staff_member):
#             return Response(
#                 {"error": "Bạn không có quyền thực hiện chức năng này"},
#                 status=status.HTTP_403_FORBIDDEN
#             )
#
#         try:
#             product = get_object_or_404(Product, pk=product_id)
#             images = request.FILES.getlist('images')
#
#             if not images:
#                 return Response(
#                     {"error": "Không có file ảnh nào được cung cấp"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#
#             created_images = []
#             for image in images:
#                 product_image = ProductImage.objects.create(product=product, image=image)
#                 created_images.append(product_image)
#
#             serializer = ProductImageSerializer(created_images, many=True)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             logger.error(f"Error adding product images: {str(e)}")
#             return Response(
#                 {"error": f"Lỗi khi thêm ảnh sản phẩm: {str(e)}"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#     def delete(self, request, product_id, image_id):
#         """Delete a product image"""
#         # Only admin_site and staff can delete images
#         if not request.user.is_authenticated or not (request.user.is_admin_user or request.user.is_staff_member):
#             return Response(
#                 {"error": "Bạn không có quyền thực hiện chức năng này"},
#                 status=status.HTTP_403_FORBIDDEN
#             )
#
#         try:
#             product = get_object_or_404(Product, pk=product_id)
#             image = get_object_or_404(ProductImage, pk=image_id, product=product)
#             image.delete()  # This will handle S3 deletion via the model's delete method
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except Exception as e:
#             logger.error(f"Error deleting product image: {str(e)}")
#             return Response(
#                 {"error": f"Lỗi khi xóa ảnh sản phẩm: {str(e)}"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )


class ProductBySlugView(APIView):
    """
    API view to get a product by its slug
    """

    def get(self, request, slug):
        """Get a specific product by slug"""
        try:
            product = get_object_or_404(Product, slug=slug)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving product by slug: {str(e)}")
            return Response(
                {"error": f"Lỗi khi lấy thông tin sản phẩm: {str(e)}"},
                status=status.HTTP_404_NOT_FOUND
            )


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


class ProductColorsView(APIView):
    def get(self, request, product_id=None):
        """Get available colors for a product or all products"""
        if product_id:
            # Get colors for a specific product
            try:
                product = Product.objects.get(pk=product_id)
                colors = Stock.objects.filter(
                    product=product,
                    color__isnull=False,
                    quantity__gt=0
                ).values_list('color', flat=True).distinct()

                data = {
                    'product_id': product.id,
                    'product_name': product.name,
                    'colors': list(colors)
                }
                serializer = ProductColorSerializer(data)
                return Response(serializer.data)
            except Product.DoesNotExist:
                return Response(
                    {"error": "Product not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Get colors for all products
            products = Product.objects.all()
            result = []

            for product in products:
                colors = Stock.objects.filter(
                    product=product,
                    color__isnull=False,
                    quantity__gt=0
                ).values_list('color', flat=True).distinct()

                if colors:  # Only include products with colors
                    data = {
                        'product_id': product.id,
                        'product_name': product.name,
                        'colors': list(colors)
                    }
                    result.append(data)

            serializer = ProductColorSerializer(result, many=True)
            return Response(serializer.data)


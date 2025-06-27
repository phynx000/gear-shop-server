from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response

from ...models.stock import Stock
from ...permissions import IsStaffUser, IsAdminUser
from ..serializers.stock_serializer import ProductInStockSerializer, StaffBranchWithStockSerializer, \
    StockUpdateSerializer
from ...models.branch import Branch


class StaffBranchesWithStockView(APIView):
    permission_classes = [IsStaffUser]  # Restricts access to staff users only

    def get(self, request):
        """Return all branches with their available stock"""
        branches = Branch.objects.all().prefetch_related(
            'stock_set',
            'stock_set__product'
        ).order_by('name')

        serializer = StaffBranchWithStockSerializer(branches, many=True)
        return Response(serializer.data)


class StaffStockUpdateView(APIView):
    permission_classes = [IsStaffUser]  # Only staff can access

    def put(self, request, stock_id):
        """Update stock information for a specific stock item"""
        try:
            stock = get_object_or_404(Stock, id=stock_id)
            serializer = StockUpdateSerializer(stock, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Stock updated successfully",
                    "stock": {
                        "id": stock.id,
                        "product_name": stock.product.name,
                        "branch_name": stock.branch.name,
                        "color": stock.color,
                        "quantity": stock.quantity
                    }
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "error": f"Failed to update stock: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, stock_id):
        """Partially update stock information"""
        try:
            stock = get_object_or_404(Stock, id=stock_id)
            serializer = StockUpdateSerializer(stock, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Stock updated successfully",
                    "stock": {
                        "id": stock.id,
                        "product_name": stock.product.name,
                        "branch_name": stock.branch.name,
                        "color": stock.color,
                        "quantity": stock.quantity
                    }
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "error": f"Failed to update stock: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from rest_framework.views import APIView
#
# from api.models.branch import Branch
# from api.models.stock import Stock
# from api.serializer import BranchWithStockSerializer
#
#
# class BranchesWithStockView(APIView):
#     permission_classes = [AllowAny]
#
#     def get(self, request, product_id):
#         """Return branches with available stock for a specific product"""
#         # Get branches that have stock for the product
#         branches = Branch.objects.filter(
#             stock__product_id=product_id,
#             stock__quantity__gt=0
#         ).distinct()
#
#         result = []
#         for branch in branches:
#             stocks = Stock.objects.filter(
#                 branch=branch,
#                 product_id=product_id,
#                 quantity__gt=0
#             ).select_related('product')
#
#             product_data = []
#             total_quantity = 0
#
#             for stock in stocks:
#                 product_data.append({
#                     'stock_id': stock.id,
#                     'color': stock.color,
#                     'quantity': stock.quantity
#                 })
#                 total_quantity += stock.quantity  # Sum up quantities
#
#             if product_data:  # Only include branches with stock
#                 data = {
#                     'branch_id': branch.id,
#                     'branch_name': branch.name,
#                     'total_quantity': total_quantity,  # Include total in response
#                     'products': product_data
#                 }
#                 result.append(data)
#
#         serializer = BranchWithStockSerializer(result, many=True)
#         return Response(serializer.data)
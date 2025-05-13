from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from ..models.cart import CartItem
from ..serializer import CartItemSerializer
from ..services.cart_service import CartItemService


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        # Kiểm tra nếu thiếu product_id hoặc quantity không hợp lệ
        if not product_id:
            return Response({"error": "Thiếu product_id"}, status=status.HTTP_400_BAD_REQUEST)
        if quantity < 1:
            return Response({"error": "Số lượng phải lớn hơn hoặc bằng 1"}, status=status.HTTP_400_BAD_REQUEST)


        try:
            print(request)
            cart_item = CartItemService.add_item_to_cart(request.user, product_id, quantity)
            print(product_id)
            return Response({
                "message": "Đã thêm sản phẩm vào giỏ hàng",
                "product_id": cart_item.product.id,
                "quantity": cart_item.quantity,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GetCartItemsView(APIView):
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        cart_items = CartItemService.get_cart_items(user)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)


class UpdateQuantityCart(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        item_id = request.data.get("item_id")
        quantity = request.data.get("quantity")

        if not item_id or quantity is None:
            return Response(
                {"error": "Missing item_id or quantity"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity < 1:
            return Response(
                {"error": "Quantity must be greater than 0"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.quantity = quantity
            cart_item.save()
            return Response(
                {"message": "Cart item quantity updated successfully", "item": cart_item.serialize()},
                status=status.HTTP_200_OK,
            )
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart item not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

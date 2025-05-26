# views/payment_return.py

from rest_framework.views import APIView
from rest_framework.response import Response
from ..services.vnpay import VNPay
from django.conf import settings
from ..models.order import Order, OrderItem
from ..models.cart import CartItem

class VNPAYReturnView(APIView):
    def get(self, request):
        print("🔥🔥🔥 ĐÃ NHẬN REQUEST TỪ VNPAY")

        vnpay_instance = VNPay()
        vnpay_instance.responseData = request.query_params.dict()

        is_valid = vnpay_instance.validate_response(settings.VNPAY_HASH_SECRET.strip())

        if is_valid and vnpay_instance.responseData.get("vnp_ResponseCode") == "00":
            txn_ref = vnpay_instance.responseData.get("vnp_TxnRef")
            order_id = txn_ref.split('_')[0] if '_' in txn_ref else txn_ref
            transaction_id = vnpay_instance.responseData.get("vnp_TransactionNo")

            try:
                order = Order.objects.get(id=order_id)
                print(order_id)
                order.vnp_transaction_id = transaction_id
                order.status = "Completed"
                order.save()

                # ✅ Lấy danh sách product_id đã đặt hàng
                product_ids = OrderItem.objects.filter(order=order).values_list('product_id', flat=True)

                # ✅ Xóa các CartItem cùng user và product
                # CartItem.objects.filter(user=order.user, product_id__in=product_ids).delete()  # đoạn này lỗi

                CartItem.objects.filter(cart__user=order.user, product_id__in=product_ids).delete()

                return Response({"message": "Thanh toán thành công" , "order_id": order_id})
            except Order.DoesNotExist:
                return Response({"error": "Đơn hàng không tồn tại"}, status=404)
        else:
            error_message = "Thanh toán thất bại hoặc sai chữ ký"
            if "vnp_ResponseCode" in vnpay_instance.responseData:
                error_code = vnpay_instance.responseData.get("vnp_ResponseCode")
                error_message += f" (Mã lỗi: {error_code})"
            return Response({"error": error_message}, status=400)

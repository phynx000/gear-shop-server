# # views/order.py
# from rest_framework.decorators import action
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status, viewsets
#
# from api.serializers.orders_serializers import OrderCreateSerializer
#
#
# class CreateOrderView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         serializer = OrderCreateSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             order = serializer.save()
#             return Response({
#                 "message": "Đơn hàng đã được tạo",
#                 "order_id": order.id,
#                 "status": order.status,
#                 "total_price": order.total_price,
#                 "payment_method": order.payment_method
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#

# views/payment.py

from django.conf import settings
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..serializers.orders_serializers import OrderCreateSerializer
from ..services.vnpay import VNPay


# Ví dụ về cách sử dụng trong view class
class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()

            if order.payment_method == "VNPAY":
                vnp_url = self.build_vnpay_url(order, request)
                return Response({
                    "message": "Đơn hàng đã được tạo",
                    "payment_url": vnp_url
                }, status=status.HTTP_201_CREATED)

            return Response({
                "message": "Đơn hàng đã được tạo",
                "order_id": order.id,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def build_vnpay_url(self, order, request):
        """
        Build the VNPAY payment URL using the official VNPay class
        """
        # Convert to VND and ensure it's an integer with no decimal places
        amount = int(order.total_price * 100)

        # Create unique transaction reference (order ID + timestamp)
        txn_ref = f"{order.id}_{int(datetime.now().timestamp())}"

        # Current date formatted according to VNPAY requirements
        create_date = datetime.now().strftime("%Y%m%d%H%M%S")

        # Initialize VNPAY object
        vnpay_instance = VNPay()
        vnpay_instance.requestData = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": settings.VNPAY_TMN_CODE,
            "vnp_Amount": amount,
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": txn_ref,
            "vnp_OrderInfo": f"Thanh toan don hang {order.id}",
            "vnp_OrderType": "other",
            "vnp_Locale": "vn",
            "vnp_ReturnUrl": settings.VNPAY_RETURN_URL,
            "vnp_IpAddr": request.META.get('REMOTE_ADDR', '127.0.0.1'),
            "vnp_CreateDate": create_date,
        }

        # Save transaction reference to order for verification
        order.reference_number = txn_ref
        order.save()

        # Get payment URL
        payment_url = vnpay_instance.get_payment_url(
            settings.VNPAY_PAYMENT_URL,
            settings.VNPAY_HASH_SECRET.strip()
        )

        # print(f"VNPAY Payment URL: {payment_url}")
        return payment_url
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from ..services.discount_service import CouponService


class ApplyCouponView(APIView):
    def post(self, request):
        code = request.data.get("code")
        total_price = float(request.data.get("total_price", 0))
        result = CouponService.validate_coupon(code, total_price)
        if result["valid"]:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response({"message": result["error"]}, status=status.HTTP_400_BAD_REQUEST)
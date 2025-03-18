from rest_framework.response import Response
from rest_framework.views import APIView
from ..serializer import FlashSaleSerializer
from ..services.discount_service import FlashSaleService


class FlashSaleListView(APIView):
    def get(self, request):
        flash_sales = FlashSaleService.get_active_flash_sales()
        serializer = FlashSaleSerializer(flash_sales, many=True)
        return Response(serializer.data)

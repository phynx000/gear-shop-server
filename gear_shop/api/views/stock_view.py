from rest_framework import generics
from ..models.stock import Stock
from ..serializer import StockSerializer
from rest_framework.permissions import IsAdminUser, AllowAny

class StockListCreateView(generics.ListCreateAPIView):
    queryset = Stock.objects.select_related('product', 'branch')
    serializer_class = StockSerializer
    permission_classes = [IsAdminUser]  # chỉ admin được thêm stock

class StockByProductView(generics.ListAPIView):
    serializer_class = StockSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        return Stock.objects.filter(product_id=product_id).select_related('branch')
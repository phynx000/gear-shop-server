from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Q

from ..models import Product
from ..models.administrative import Province, District, Ward
from ..models.branch import Branch
from ..models.stock import Stock
from ..serializer import ProvinceSerializer, DistrictSerializer, WardSerializer, BranchWithStockSerializer


class ProvinceListView(generics.ListAPIView):
    """Lấy danh sách tất cả tỉnh/thành phố"""
    queryset = Province.objects.all().order_by('name')
    serializer_class = ProvinceSerializer


class DistrictListView(generics.ListAPIView):
    """Lấy danh sách quận/huyện theo tỉnh"""
    serializer_class = DistrictSerializer

    def get_queryset(self):
        province_id = self.request.query_params.get('province_id')
        if province_id:
            return District.objects.filter(province_id=province_id).order_by('name')
        return District.objects.none()


class WardListView(generics.ListAPIView):
    """Lấy danh sách ph
    ường/xã theo quận/huyện"""
    serializer_class = WardSerializer

    def get_queryset(self):
        district_id = self.request.query_params.get('district_id')
        if district_id:
            return Ward.objects.filter(district_id=district_id).order_by('name')
        return Ward.objects.none()


@api_view(['GET'])
def branches_with_stock(request):
    """
    Lấy danh sách chi nhánh có hàng theo điều kiện lọc
    Query params:
    - product_id: ID sản phẩm (bắt buộc)
    - province_id: ID tỉnh/thành (tùy chọn)
    - district_id: ID quận/huyện (tùy chọn)
    - color: Màu sắc (tùy chọn)
    """
    product_id = request.query_params.get('product_id')
    if not product_id:
        return Response(
            {'error': 'product_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Kiểm tra sản phẩm có tồn tại không
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Lọc các chi nhánh có tồn kho > 0
    stock_filter = Q(stock__product_id=product_id, stock__quantity__gt=0)

    # Thêm filter theo tỉnh nếu có
    province_id = request.query_params.get('province_id')
    if province_id:
        stock_filter &= Q(province_id=province_id)

    # Thêm filter theo quận/huyện nếu có
    district_id = request.query_params.get('district_id')
    if district_id:
        stock_filter &= Q(district_id=district_id)

    # Thêm filter theo màu nếu có
    color = request.query_params.get('color')
    if color:
        stock_filter &= Q(stock__color=color)

    # Lấy danh sách chi nhánh
    branches = Branch.objects.filter(stock_filter).distinct().select_related(
        'province', 'district', 'ward'
    ).order_by('name')

    # Serialize data
    serializer = BranchWithStockSerializer(
        branches,
        many=True,
        context={'product_id': product_id}
    )

    return Response({
        'product': {
            'id': product.id,
            'name': product.name
        },
        'branches': serializer.data,
        'total_branches': len(serializer.data)
    })


@api_view(['GET'])
def available_colors_by_location(request):
    """
    Lấy danh sách màu có sẵn theo địa điểm và thông tin số lượng
    Query params:
    - product_id: ID sản phẩm (bắt buộc)
    - province_id: ID tỉnh/thành (tùy chọn)
    - district_id: ID quận/huyện (tùy chọn)
    - color: Màu sắc (tùy chọn)
    """
    product_id = request.query_params.get('product_id')
    if not product_id:
        return Response(
            {'error': 'product_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Base filter
    stock_filter = Q(product_id=product_id, quantity__gt=0)

    # Thêm filter theo địa điểm
    province_id = request.query_params.get('province_id')
    if province_id:
        stock_filter &= Q(branch__province_id=province_id)

    district_id = request.query_params.get('district_id')
    if district_id:
        stock_filter &= Q(branch__district_id=district_id)

    # Thêm filter theo màu sắc nếu có
    color = request.query_params.get('color')
    if color:
        stock_filter &= Q(color=color)

    # Lấy danh sách màu có sẵn
    colors = Stock.objects.filter(stock_filter).values_list(
        'color', flat=True
    ).distinct().order_by('color')

    # Tính tổng số lượng tồn kho theo chi nhánh (tất cả màu)
    branch_totals = Stock.objects.filter(stock_filter).values(
        'branch', 'branch__name'
    ).annotate(
        total_quantity=Sum('quantity')
    ).order_by('branch__name')

    # Tính số lượng tồn kho theo màu và chi nhánh
    color_quantities = Stock.objects.filter(stock_filter).values(
        'branch', 'branch__name', 'color'
    ).annotate(
        quantity=Sum('quantity')
    ).order_by('branch__name', 'color')

    return Response({
        'colors': list(colors),
        'branch_totals': branch_totals,
        'color_quantities': color_quantities
    })
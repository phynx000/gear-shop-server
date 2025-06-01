# gear_shop/api/views/search_view.py
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Case, When, IntegerField
from ..models.products import Product, Category, Brand
from ..serializer import ProductSerializer


@api_view(['GET'])
def search_products(request):
    """
    API tìm kiếm sản phẩm theo từ khóa với độ ưu tiên thông minh
    """
    # Lấy tham số từ query string
    query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '')
    brand_filter = request.GET.get('brand', '')
    limit = int(request.GET.get('limit', 50))
    sort_by = request.GET.get('sort', 'relevance')  # Mặc định sắp xếp theo độ liên quan

    # Kiểm tra từ khóa tìm kiếm
    if not query:
        return Response({
            'error': 'Vui lòng nhập từ khóa tìm kiếm',
            'message': 'Tham số "q" là bắt buộc'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Tách từ khóa thành các từ riêng biệt
    keywords = query.lower().split()

    # Khởi tạo query set
    products = Product.objects.all()

    # Tạo điều kiện tìm kiếm với độ ưu tiên
    primary_conditions = Q()  # Tìm kiếm chính xác (độ ưu tiên cao)
    secondary_conditions = Q()  # Tìm kiếm mở rộng (độ ưu tiên thấp)

    for keyword in keywords:
        # ĐIỀU KIỆN ƯU TIÊN CAO (tìm kiếm chính xác)
        # 1. Tên sản phẩm chứa từ khóa
        exact_name = Q(name__icontains=keyword)

        # 2. Tên danh mục chứa từ khóa
        exact_category = Q(category__name__icontains=keyword)

        # 3. Tên thương hiệu chứa từ khóa
        exact_brand = Q(brand__name__icontains=keyword)

        # 4. Product group chứa từ khóa
        exact_group = Q(product_group__icontains=keyword)

        # 5. SKU chứa từ khóa
        exact_sku = Q(sku__icontains=keyword)

        # ĐIỀU KIỆN ƯU TIÊN THẤP (tìm kiếm mở rộng)
        # 1. Mô tả sản phẩm chứa từ khóa
        desc_condition = Q(description__icontains=keyword)

        # 2. Thông số kỹ thuật chứa từ khóa
        spec_condition = Q(specification__value__icontains=keyword) | Q(specification__key__icontains=keyword)

        # 3. Version chứa từ khóa
        version_condition = Q(version__icontains=keyword)

        # Kết hợp điều kiện ưu tiên cao
        high_priority = exact_name | exact_category | exact_brand | exact_group | exact_sku

        # Kết hợp điều kiện ưu tiên thấp
        low_priority = desc_condition | spec_condition | version_condition

        # Kết hợp với điều kiện tổng thể (AND giữa các từ khóa)
        if not primary_conditions:
            primary_conditions = high_priority
            secondary_conditions = low_priority
        else:
            primary_conditions &= high_priority
            secondary_conditions &= low_priority

    # Tìm sản phẩm có độ ưu tiên cao trước
    high_priority_products = products.filter(primary_conditions).distinct()

    # Nếu không đủ kết quả, thêm sản phẩm có độ ưu tiên thấp
    low_priority_products = products.filter(secondary_conditions).distinct().exclude(
        id__in=high_priority_products.values_list('id', flat=True)
    )

    # Lọc theo danh mục nếu có
    if category_filter:
        category_q = Q(category__name__icontains=category_filter) | Q(category__slug__icontains=category_filter)
        high_priority_products = high_priority_products.filter(category_q)
        low_priority_products = low_priority_products.filter(category_q)

    # Lọc theo thương hiệu nếu có
    if brand_filter:
        brand_q = Q(brand__name__icontains=brand_filter)
        high_priority_products = high_priority_products.filter(brand_q)
        low_priority_products = low_priority_products.filter(brand_q)

    # Sắp xếp kết quả
    def apply_sorting(queryset, sort_type):
        if sort_type == 'name_asc':
            return queryset.order_by('name')
        elif sort_type == 'name_desc':
            return queryset.order_by('-name')
        elif sort_type == 'price_asc':
            return queryset.order_by('original_price')
        elif sort_type == 'price_desc':
            return queryset.order_by('-original_price')
        elif sort_type == 'newest':
            return queryset.order_by('-created_at')
        else:  # relevance hoặc mặc định
            return queryset.order_by('-created_at')

    high_priority_products = apply_sorting(high_priority_products, sort_by)
    low_priority_products = apply_sorting(low_priority_products, sort_by)

    # Kết hợp kết quả với độ ưu tiên
    final_results = []

    # Lấy sản phẩm độ ưu tiên cao trước
    high_priority_list = list(high_priority_products[:limit])
    final_results.extend(high_priority_list)

    # Nếu chưa đủ, lấy thêm sản phẩm độ ưu tiên thấp
    remaining_limit = limit - len(high_priority_list)
    if remaining_limit > 0:
        low_priority_list = list(low_priority_products[:remaining_limit])
        final_results.extend(low_priority_list)

    # Serialize dữ liệu
    serializer = ProductSerializer(final_results, many=True)

    # Tính tổng số kết quả
    total_high_priority = high_priority_products.count()
    total_low_priority = low_priority_products.count()
    total_results = total_high_priority + total_low_priority

    return Response({
        'query': query,
        'total_results': total_results,
        'high_priority_results': total_high_priority,
        'low_priority_results': total_low_priority,
        'returned_results': len(serializer.data),
        'results': serializer.data,
        'filters_applied': {
            'category': category_filter if category_filter else None,
            'brand': brand_filter if brand_filter else None,
            'sort': sort_by,
            'limit': limit
        },
        'search_info': {
            'message': f'Tìm thấy {total_high_priority} kết quả chính xác và {total_low_priority} kết quả liên quan',
            'suggestion': 'Kết quả được sắp xếp theo độ liên quan, sản phẩm chính xác hiển thị trước'
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def search_products_strict(request):
    """
    API tìm kiếm sản phẩm nghiêm ngặt - chỉ tìm trong tên, danh mục, thương hiệu
    """
    query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '')
    brand_filter = request.GET.get('brand', '')
    limit = int(request.GET.get('limit', 50))
    sort_by = request.GET.get('sort', 'newest')

    if not query:
        return Response({
            'error': 'Vui lòng nhập từ khóa tìm kiếm',
            'message': 'Tham số "q" là bắt buộc'
        }, status=status.HTTP_400_BAD_REQUEST)

    keywords = query.lower().split()
    products = Product.objects.all()
    search_conditions = Q()

    for keyword in keywords:
        # CHỈ tìm kiếm trong các trường chính
        keyword_condition = (
                Q(name__icontains=keyword) |
                Q(category__name__icontains=keyword) |
                Q(brand__name__icontains=keyword) |
                Q(product_group__icontains=keyword) |
                Q(sku__icontains=keyword)
        )

        if not search_conditions:
            search_conditions = keyword_condition
        else:
            search_conditions &= keyword_condition

    products = products.filter(search_conditions).distinct()

    # Áp dụng các bộ lọc khác
    if category_filter:
        products = products.filter(
            Q(category__name__icontains=category_filter) |
            Q(category__slug__icontains=category_filter)
        )

    if brand_filter:
        products = products.filter(brand__name__icontains=brand_filter)

    # Sắp xếp
    if sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')
    elif sort_by == 'price_asc':
        products = products.order_by('original_price')
    elif sort_by == 'price_desc':
        products = products.order_by('-original_price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')

    products = products[:limit]
    serializer = ProductSerializer(products, many=True)
    total_results = Product.objects.filter(search_conditions).distinct().count()

    return Response({
        'query': query,
        'total_results': total_results,
        'returned_results': len(serializer.data),
        'results': serializer.data,
        'search_type': 'strict',
        'filters_applied': {
            'category': category_filter if category_filter else None,
            'brand': brand_filter if brand_filter else None,
            'sort': sort_by,
            'limit': limit
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def search_suggestions(request):
    """
    API gợi ý tìm kiếm (autocomplete) - cải thiện độ chính xác
    """
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 10))

    if len(query) < 2:
        return Response({'suggestions': []})

    suggestions = []

    # Ưu tiên gợi ý từ tên sản phẩm (khớp từ đầu)
    products_startswith = Product.objects.filter(
        name__istartswith=query
    ).values_list('name', flat=True)[:limit // 2]

    suggestions.extend([{
        'text': name,
        'type': 'product',
        'priority': 'high'
    } for name in products_startswith])

    # Gợi ý từ tên sản phẩm (chứa từ khóa)
    remaining_limit = limit - len(suggestions)
    if remaining_limit > 0:
        products_contains = Product.objects.filter(
            name__icontains=query
        ).exclude(
            name__istartswith=query
        ).values_list('name', flat=True)[:remaining_limit // 2]

        suggestions.extend([{
            'text': name,
            'type': 'product',
            'priority': 'medium'
        } for name in products_contains])

    # Gợi ý từ danh mục và thương hiệu
    remaining_limit = limit - len(suggestions)
    if remaining_limit > 0:
        categories = Category.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:remaining_limit // 2]

        brands = Brand.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:remaining_limit // 2]

        suggestions.extend([{
            'text': name,
            'type': 'category',
            'priority': 'low'
        } for name in categories])

        suggestions.extend([{
            'text': name,
            'type': 'brand',
            'priority': 'low'
        } for name in brands])

    return Response({
        'query': query,
        'suggestions': suggestions[:limit]
    })


@api_view(['GET'])
def get_search_filters(request):
    """
    API lấy danh sách các bộ lọc có thể sử dụng
    """
    categories = Category.objects.all().values('id', 'name', 'slug')
    brands = Brand.objects.all().values('id', 'name')

    return Response({
        'categories': list(categories),
        'brands': list(brands),
        'sort_options': [
            {'value': 'relevance', 'label': 'Độ liên quan'},
            {'value': 'newest', 'label': 'Mới nhất'},
            {'value': 'name_asc', 'label': 'Tên A-Z'},
            {'value': 'name_desc', 'label': 'Tên Z-A'},
            {'value': 'price_asc', 'label': 'Giá thấp đến cao'},
            {'value': 'price_desc', 'label': 'Giá cao đến thấp'},
        ],
        'search_modes': [
            {'value': 'smart', 'label': 'Tìm kiếm thông minh', 'description': 'Kết hợp tìm kiếm chính xác và mở rộng'},
            {'value': 'strict', 'label': 'Tìm kiếm nghiêm ngặt',
             'description': 'Chỉ tìm trong tên, danh mục, thương hiệu'}
        ]
    })
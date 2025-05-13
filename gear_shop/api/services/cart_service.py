from django.shortcuts import get_object_or_404
from ..models.cart import Cart, CartItem
from ..models.products import Product


class CartService:
    @staticmethod
    def get_or_create_cart(user):
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

class CartItemService:

    # @staticmethod
    # def add_item_to_cart(user, product_id, quantity=1):
    #     if quantity < 1:
    #         raise ValueError("Số lượng phải lớn hơn hoặc bằng 1")
    #
    #     cart = CartService.get_or_create_cart(user)
    #     product = get_object_or_404(Product, id=product_id)
    #
    #     # Kiểm tra sản phẩm đã có trong giỏ hay chưa
    #     cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    #
    #     if created:
    #         # Nếu là sản phẩm mới, gán số lượng ban đầu
    #         cart_item.quantity = quantity
    #     else:
    #         # Nếu sản phẩm đã có trong giỏ, cập nhật số lượng
    #         cart_item.quantity += quantity
    #
    #     cart_item.save()
    #     return cart_item

    @staticmethod
    def add_item_to_cart(user, product_id, quantity=1):
        cart = CartService.get_or_create_cart(user)
        product = get_object_or_404(Product, id=product_id)

        if quantity is None or quantity < 1:
            raise ValueError("Số lượng không hợp lệ")

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}  # nếu là item mới thì gán luôn
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item

    @staticmethod
    def get_cart_items(user):
        cart = CartService.get_or_create_cart(user)
        return CartItem.objects.filter(cart=cart).select_related('product')

    @staticmethod
    def update_item_in_cart(user, product_id, quantity):
        # Lấy giỏ hàng của người dùng hoặc tạo mới nếu không có
        cart = CartService.get_or_create_cart(user)

        # Lấy sản phẩm từ cơ sở dữ liệu
        product = get_object_or_404(Product, id=product_id)

        # Tìm CartItem liên quan đến sản phẩm trong giỏ hàng
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)

        # Cập nhật số lượng sản phẩm
        if quantity < 1:
            # Xóa sản phẩm nếu số lượng nhỏ hơn 1
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        return cart_item


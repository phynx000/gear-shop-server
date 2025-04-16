from django.utils.timezone import now
from ..models.coupon import Coupon
from ..models.flash_sale import FlashSale



class CouponService:
    @staticmethod
    def validate_coupon(code, total_price):
        """
        Kiểm tra mã giảm giá hợp lệ và tính toán số tiền giảm giá.
        """
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)

            if coupon.expires_at < now():
                return {"error": "Mã giảm giá đã hết hạn", "valid": False}

            if total_price < coupon.min_order_amount:
                return {
                    "error": f"Đơn hàng phải trên {coupon.min_order_amount} để áp dụng mã giảm giá",
                    "valid": False,
                }

            discount = coupon.discount_value
            if coupon.discount_type == "percent":
                discount = (total_price * discount) / 100
                if coupon.max_discount and discount > coupon.max_discount:
                    discount = coupon.max_discount  # Giới hạn mức giảm tối đa

            new_price = total_price - discount
            return {"discount": discount, "new_price": new_price, "valid": True}

        except Coupon.DoesNotExist:
            return {"error": "Mã giảm giá không hợp lệ", "valid": False}


class FlashSaleService():
    @staticmethod
    def get_active_flash_sales():
        """
        Lấy danh sách Flash Sale đang hoạt động.
        """
        return FlashSale.objects.filter(is_active=True, start_time__lte=now(), end_time__gte=now())
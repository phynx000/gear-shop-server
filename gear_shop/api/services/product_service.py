from ..models.products import Product, ProductImage


class ProductService:
    @staticmethod
    def get_all_products():
        return Product.objects.prefetch_related("images").all()

    @staticmethod
    def get_product_by_id(product_id):
        return Product.objects.prefetch_related("images").all()

    @staticmethod
    def get_product_by_name(name):
        return Product.objects.get(name=name)

    @staticmethod
    def get_product_by_category(category_id):
        return Product.objects.prefetch_related("images").filter(category_id=category_id)

    @staticmethod
    def get_product_by_brand(brand_id):
        return Product.objects.filter(brand_id=brand_id)

    @staticmethod
    def create_product(data):
        return Product.objects.create(**data)

    @staticmethod
    def get_product_image_by_product(product_id):
        return ProductImage.objects.filter(product_id=product_id)


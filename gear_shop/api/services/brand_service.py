from ..models.products import Brand

class BrandService:
    @staticmethod
    def get_all_brands():
        return Brand.objects.all()

    def get_brands_by_category_service(category_id):
        brands = Brand.objects.filter(product__category_id=category_id).distinct()
        return [{"id": brand.id, "name": brand.name} for brand in brands]

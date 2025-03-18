from ..models.products import Brand

class BrandService:
    @staticmethod
    def get_all_brands():
        return Brand.objects.all()

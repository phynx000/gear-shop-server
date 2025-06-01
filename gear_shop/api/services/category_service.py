from ..models.products import Category


class CategoryService:
    @staticmethod
    def get_all_category():
        return Category.objects.all()

    @staticmethod
    def get_category_by_id(category_id):
        try:
            return Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return None


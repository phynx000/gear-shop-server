from ..models.specification import Specification

class SpecificationService:
    def get_specification_by_id(self, specification_id):
        return Specification.objects.get(id=specification_id)